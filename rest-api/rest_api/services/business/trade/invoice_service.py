import re
from io import BytesIO
from typing import TypeAlias
from xml.sax.saxutils import escape

from config.settings import Settings
from models.business.trade.invoice import Invoice
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from repositories.business.trade.invoice_repository import InvoiceRepository
from schemas.business.trade.invoice_schema import InvoicePlainSchema, InvoiceStrictSchema
from services.base.base_service import BaseService
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

TableCell: TypeAlias = str | Paragraph
TableRow: TypeAlias = list[TableCell]


class InvoiceService(BaseService[Invoice, InvoiceRepository, InvoiceStrictSchema, InvoicePlainSchema]):
    _repository_cls = InvoiceRepository
    _model_cls = Invoice
    _output_schema_cls = InvoicePlainSchema

    __font_regular = "DejaVuSans"
    __font_bold = "DejaVuSans-Bold"
    __font_regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    __font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__()
        self.__settings = settings or Settings()  # type: ignore
        self.__register_fonts()

    async def build_invoice_pdf(self, session: AsyncSession, invoice_id: int) -> tuple[bytes, str]:
        invoice = await self._repository_cls.get_invoice_with_relations(session, invoice_id)
        if invoice is None:
            raise NoResultFound(f"Invoice with ID {invoice_id} not found.")
        return self.__render(invoice), self.__build_filename(invoice.number)

    def __render(self, invoice: Invoice) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )
        styles = getSampleStyleSheet()
        small_style = ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName=self.__font_regular,
            fontSize=9,
            leading=11,
        )
        title_style = ParagraphStyle(
            name="Title",
            parent=styles["Title"],
            fontName=self.__font_bold,
            fontSize=18,
            leading=20,
        )
        section_style = ParagraphStyle(
            name="Section",
            parent=styles["Heading4"],
            fontName=self.__font_bold,
            fontSize=10,
            leading=12,
        )
        elements = []
        full_width = document.width

        elements.append(Paragraph(f"Invoice {invoice.number}", title_style))
        elements.append(Spacer(1, 5 * mm))
        elements.append(Paragraph(f"Issue date: {invoice.issue_date.isoformat()}", small_style))
        elements.append(Paragraph(f"Due date: {invoice.due_date.isoformat()}", small_style))
        currency_label = "-"
        if invoice.currency:
            currency_label = invoice.currency.name or invoice.currency.code
        elements.append(Paragraph(f"Currency: {currency_label}", small_style))
        elements.append(Spacer(1, 5 * mm))
        party_table = Table(
            [
                [Paragraph("Issuer", section_style), Paragraph("Buyer", section_style)],
                [
                    Paragraph("<br/>".join(self.__build_issuer_lines()), small_style),
                    Paragraph("<br/>".join(self.__build_buyer_lines(invoice)), small_style),
                ],
            ],
            colWidths=self.__normalize_col_widths([full_width * 0.5, full_width * 0.5], full_width),
            hAlign="LEFT",
        )
        party_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(party_table)
        elements.append(Spacer(1, 5 * mm))

        table_rows: list[TableRow] = [
            ["Lp.", "Order", "Index", "Qty", "Unit", "Net", "VAT", "Gross"],
        ]
        row_number = 1
        for order in sorted(invoice.orders, key=lambda row: row.id):
            for order_item in sorted(order.order_items, key=lambda row: row.id):
                item = order_item.item
                order_label = self.__build_breakable_paragraph(order.number, small_style)
                item_index_value = item.index if item else str(order_item.item_id)
                item_index_label = self.__build_breakable_paragraph(item_index_value, small_style)
                table_rows.append(
                    [
                        str(row_number),
                        order_label,
                        item_index_label,
                        str(order_item.quantity),
                        item.unit.symbol if item and item.unit else "",
                        self.__format_number(order_item.total_net),
                        self.__format_number(order_item.total_vat),
                        self.__format_number(order_item.total_gross),
                    ]
                )
                row_number += 1

        items_col_widths = self.__normalize_col_widths(self.__build_items_col_widths(full_width), full_width)
        items_table = Table(
            table_rows,
            colWidths=items_col_widths,
            repeatRows=1,
            hAlign="LEFT",
        )
        items_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                    ("WORDWRAP", (1, 1), (2, -1), "CJK"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), self.__font_bold),
                    ("FONTNAME", (0, 1), (-1, -1), self.__font_regular),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(items_table)
        elements.append(Spacer(1, 5 * mm))

        totals_table_width = 85 * mm
        totals_table = Table(
            [
                ["Total net", self.__format_number(invoice.total_net)],
                ["Total VAT", self.__format_number(invoice.total_vat)],
                ["Total gross", self.__format_number(invoice.total_gross)],
                ["Total discount", self.__format_number(invoice.total_discount)],
            ],
            colWidths=[50 * mm, 35 * mm],
            hAlign="LEFT",
        )
        totals_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, -1), self.__font_regular),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        totals_wrapper = Table(
            [["", totals_table]],
            colWidths=self.__normalize_col_widths([full_width - totals_table_width, totals_table_width], full_width),
            hAlign="LEFT",
        )
        totals_wrapper.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        elements.append(totals_wrapper)

        if invoice.notes:
            elements.append(Spacer(1, 5 * mm))
            elements.append(Paragraph("Notes", small_style))
            elements.append(Paragraph(invoice.notes, small_style))

        document.build(elements)
        return buffer.getvalue()

    def __build_issuer_lines(self) -> list[str]:
        issuer_street_line = self.__build_street_line(
            self.__settings.ISSUER_STREET,
            self.__settings.ISSUER_HOUSE_NUMBER,
            self.__settings.ISSUER_APARTMENT_NUMBER,
        )
        issuer_city_line = self.__join_non_empty(
            [self.__settings.ISSUER_POSTAL_CODE, self.__settings.ISSUER_CITY],
            separator=" ",
        )
        lines = [
            self.__settings.ISSUER_NAME,
            f"Tax ID: {self.__settings.ISSUER_TAX_ID}" if self.__settings.ISSUER_TAX_ID else "",
            issuer_street_line,
            issuer_city_line,
            self.__settings.ISSUER_COUNTRY,
            f"E-mail: {self.__settings.ISSUER_EMAIL}" if self.__settings.ISSUER_EMAIL else "",
            f"Phone: {self.__settings.ISSUER_PHONE}" if self.__settings.ISSUER_PHONE else "",
            f"Bank: {self.__settings.ISSUER_BANK_NAME}" if self.__settings.ISSUER_BANK_NAME else "",
            (f"Account: {self.__settings.ISSUER_BANK_ACCOUNT.strip()}" if self.__settings.ISSUER_BANK_ACCOUNT else ""),
        ]
        normalized = [line.strip() for line in lines if line and line.strip()]
        return normalized if normalized else ["-"]

    @staticmethod
    def __build_buyer_lines(invoice: Invoice) -> list[str]:
        if not invoice.customer:
            return ["-"]
        street_line = InvoiceService.__build_street_line(
            invoice.customer.street or "",
            invoice.customer.house_number or "",
            invoice.customer.apartment_number or "",
        )
        city_line = InvoiceService.__join_non_empty(
            [invoice.customer.postal_code or "", invoice.customer.city or ""],
            separator=" ",
        )
        lines = [
            invoice.customer.company_name or "",
            f"Tax ID: {invoice.customer.tax_id}" if invoice.customer.tax_id else "",
            street_line,
            city_line,
            invoice.customer.country or "",
            f"E-mail: {invoice.customer.email}" if invoice.customer.email else "",
            f"Phone: {invoice.customer.phone_number}" if invoice.customer.phone_number else "",
        ]
        normalized = [line.strip() for line in lines if line and line.strip()]
        return normalized if normalized else ["-"]

    @staticmethod
    def __format_number(value: float) -> str:
        return f"{value:.2f}"

    @staticmethod
    def __build_breakable_paragraph(value: str, style: ParagraphStyle) -> Paragraph:
        escaped_value = escape(value)
        breakable_value = escaped_value.replace("/", "/&#8203;").replace("-", "-&#8203;").replace("_", "_&#8203;")
        return Paragraph(breakable_value, style)

    @staticmethod
    def __join_non_empty(parts: list[str], separator: str = " ") -> str:
        normalized = [part.strip() for part in parts if part and part.strip()]
        return separator.join(normalized)

    @staticmethod
    def __normalize_col_widths(widths: list[float], total_width: float) -> list[float]:
        if not widths:
            return widths
        normalized = widths.copy()
        width_delta = total_width - sum(normalized)
        normalized[-1] += width_delta
        return normalized

    @staticmethod
    def __build_items_col_widths(total_width: float) -> list[float]:
        width_lp = 10 * mm
        width_order = 40 * mm
        width_qty = 13 * mm
        width_unit = 12 * mm
        width_net = 20 * mm
        width_vat = 20 * mm
        width_gross = 20 * mm
        fixed_width = width_lp + width_order + width_qty + width_unit + width_net + width_vat + width_gross

        width_index = total_width - fixed_width
        min_index_width = 28 * mm
        if width_index < min_index_width:
            min_order_width = 30 * mm
            missing_width = min_index_width - width_index
            reducible_order_width = max(0.0, width_order - min_order_width)
            width_order -= min(missing_width, reducible_order_width)
            fixed_width = width_lp + width_order + width_qty + width_unit + width_net + width_vat + width_gross
            width_index = max(min_index_width, total_width - fixed_width)

        return [width_lp, width_order, width_index, width_qty, width_unit, width_net, width_vat, width_gross]

    @staticmethod
    def __build_street_line(street: str, house_number: str, apartment_number: str) -> str:
        normalized_street = street.strip()
        normalized_house = house_number.strip()
        normalized_apartment = apartment_number.strip()
        house_and_apartment = normalized_house
        if normalized_house and normalized_apartment:
            house_and_apartment = f"{normalized_house}/{normalized_apartment}"
        elif not normalized_house and normalized_apartment:
            house_and_apartment = normalized_apartment
        return InvoiceService.__join_non_empty([normalized_street, house_and_apartment], separator=" ")

    @staticmethod
    def __build_filename(number: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9_.-]+", "_", number).strip("_")
        if not normalized:
            normalized = "invoice"
        return f"{normalized}.pdf"

    def __register_fonts(self) -> None:
        if self.__font_regular not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(self.__font_regular, self.__font_regular_path))
        if self.__font_bold not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(self.__font_bold, self.__font_bold_path))
