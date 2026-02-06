# Excel Column Mapping - EXACT Names (No Assumptions)

## Source: Sales Analysis FY 2025-26.xlsx - Sheet1

### All Columns (31 total):

1. **Transaction Type** - Type of transaction (Sale, Sale Return)
2. **VchNo** - Voucher number
3. **VchDate** - Voucher date
4. **Vch Series** - Voucher series
5. **Tax Type** - Tax type (IGST, CGST, etc.)
6. **Party Name** - Party name
7. **Billed Party Name** - Billed party name
8. **Item Desc** - Product description (PRODUCT NAME)
9. **Alias** - Product alias/SKU code (SKU)
10. **Group Name** - Product category (CATEGORY)
11. **NameAlias** - Name alias
12. **HSNCode** - HSN code
13. **Qty.** - Quantity (note the space and period)
14. **Order ID** - Order ID
15. **Narration** - Narration
16. **Tax Rate** - Tax rate
17. **Taxable Value** - Taxable value
18. **Tax Value** - Tax value
19. **Invoice Amt** - Invoice amount
20. **OrgVchNo** - Original voucher number
21. **StockUpdationDate** - Stock update date
22. **Org..VchDate** - Original voucher date
23. **Final Order date** - PRIMARY DATE FOR ANALYSIS
24. **Sale (Qty.)** - Sale quantity
25. **Sale Return (Qty.)** - Sale return quantity
26. **Sale (Amt.)** - Sale amount
27. **Sale Return (Amt.)** - Sale return amount
28. **Main Parties** - PLATFORM (Amazon, Flipkart, etc.)
29. **Refund Reasons** - Refund reasons
30. **Dispatch Coruier partner** - Dispatch courier partner (note typo: "Coruier")
31. **Dispatch Status** - Dispatch status

## Dashboard Column Mapping

### Primary Columns to Use:

| Dashboard Field | Excel Column | Notes |
|----------------|--------------|-------|
| **Date** | `Final Order date` | Primary date for all analysis |
| **Platform** | `Main Parties` | Amazon, Flipkart, etc. |
| **Category** | `Group Name` | Product category |
| **Product** | `Item Desc` | Full product name |
| **SKU** | `Alias` | Product SKU/alias |
| **Revenue** | `Sale (Amt.)` | Gross sales amount |
| **Returns** | `Sale Return (Amt.)` | Return amount |
| **Quantity** | `Sale (Qty.)` | Units sold |
| **Return Qty** | `Sale Return (Qty.)` | Units returned |
| **Dispatch Status** | `Dispatch Status` | Delivery status |
| **Courier** | `Dispatch Coruier partner` | Courier name |

### Calculated Fields:

- **Net Revenue** = `Sale (Amt.)` - `Sale Return (Amt.)`
- **Net Quantity** = `Sale (Qty.)` - `Sale Return (Qty.)`
- **Fiscal Year** = Calculated from `Final Order date` (Mar-Feb)
- **Month** = Extracted from `Final Order date`

## Columns NOT Used (Can Ignore):

- VchNo, VchDate, Vch Series
- Tax Type, Tax Rate, Taxable Value, Tax Value
- Party Name, Billed Party Name (use Main Parties instead)
- NameAlias, HSNCode
- Order ID, Narration
- Invoice Amt
- OrgVchNo, StockUpdationDate, Org..VchDate
- Refund Reasons (mostly empty)
- Qty. (use Sale (Qty.) instead)
