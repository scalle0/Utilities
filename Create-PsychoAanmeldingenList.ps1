<#
.SYNOPSIS
    Creates the "Psycho Aanmeldingen" Microsoft/SharePoint List.

.DESCRIPTION
    Provisions a SharePoint list with all columns for tracking psychology referrals.
    Requires the PnP.PowerShell module and an active connection to your SharePoint site.

.EXAMPLE
    # First connect to your SharePoint site:
    Connect-PnPOnline -Url "https://yourtenant.sharepoint.com/sites/yoursite" -Interactive

    # Then run this script:
    .\Create-PsychoAanmeldingenList.ps1
#>

param(
    [string]$ListName = "Psycho Aanmeldingen"
)

# --- Verify PnP connection ---
try {
    $ctx = Get-PnPContext
    if (-not $ctx) { throw }
    Write-Host "Connected to: $($ctx.Url)" -ForegroundColor Green
}
catch {
    Write-Error "No active PnP connection. Run 'Connect-PnPOnline -Url <your-site-url> -Interactive' first."
    exit 1
}

# --- Create the list ---
Write-Host "`nCreating list '$ListName'..." -ForegroundColor Cyan
$list = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue
if ($list) {
    Write-Warning "List '$ListName' already exists. Skipping creation."
}
else {
    New-PnPList -Title $ListName -Template GenericList
    Write-Host "List created." -ForegroundColor Green
}

# ============================================================
# COLUMNS
# ============================================================

# 1. Naam (single line of text) — uses the built-in Title column
Write-Host "Renaming Title column to 'Naam'..." -ForegroundColor Cyan
Set-PnPField -List $ListName -Identity "Title" -Values @{Title = "Naam"} -ErrorAction SilentlyContinue

# 2. Adrema
Write-Host "Adding column: Adrema..." -ForegroundColor Cyan
Add-PnPField -List $ListName -DisplayName "Adrema" -InternalName "Adrema" -Type Text -ErrorAction SilentlyContinue

# 3. Aanvrager
Write-Host "Adding column: Aanvrager..." -ForegroundColor Cyan
Add-PnPField -List $ListName -DisplayName "Aanvrager" -InternalName "Aanvrager" -Type Text -ErrorAction SilentlyContinue

# 4. In opvolging voor (Choice: PrEP / Hiv)
Write-Host "Adding column: In opvolging voor..." -ForegroundColor Cyan
Add-PnPFieldFromXml -List $ListName -FieldXml @"
<Field Type="Choice"
       DisplayName="In opvolging voor"
       Name="InOpvolgingVoor"
       Format="Dropdown"
       FillInChoice="FALSE">
  <CHOICES>
    <CHOICE>PrEP</CHOICE>
    <CHOICE>Hiv</CHOICE>
  </CHOICES>
</Field>
"@ -ErrorAction SilentlyContinue

# 5. Soort aanmelding (Choice)
Write-Host "Adding column: Soort aanmelding..." -ForegroundColor Cyan
Add-PnPFieldFromXml -List $ListName -FieldXml @"
<Field Type="Choice"
       DisplayName="Soort aanmelding"
       Name="SoortAanmelding"
       Format="Dropdown"
       FillInChoice="FALSE">
  <CHOICES>
    <CHOICE>Nieuwe aanmelding</CHOICE>
    <CHOICE>Gekende patiënt in psycho opvolging</CHOICE>
  </CHOICES>
</Field>
"@ -ErrorAction SilentlyContinue

# 6. Formuleer hulpvraag (Multi-line text)
Write-Host "Adding column: Formuleer hulpvraag..." -ForegroundColor Cyan
Add-PnPField -List $ListName -DisplayName "Formuleer hulpvraag" -InternalName "FormuleerHulpvraag" -Type Note -ErrorAction SilentlyContinue

# 7. Na-actie (Choice)
Write-Host "Adding column: Na-actie..." -ForegroundColor Cyan
Add-PnPFieldFromXml -List $ListName -FieldXml @"
<Field Type="Choice"
       DisplayName="Na-actie"
       Name="NaActie"
       Format="Dropdown"
       FillInChoice="FALSE">
  <CHOICES>
    <CHOICE>Inboeken agenda Charlotte</CHOICE>
    <CHOICE>Inboeken agenda Lien</CHOICE>
    <CHOICE>Extern doorverwezen</CHOICE>
    <CHOICE>Wachtlijst</CHOICE>
    <CHOICE>TC (telefonisch contact)</CHOICE>
  </CHOICES>
</Field>
"@ -ErrorAction SilentlyContinue

# 8. Status na-actie (Choice with color-code support)
Write-Host "Adding column: Status na-actie..." -ForegroundColor Cyan
Add-PnPFieldFromXml -List $ListName -FieldXml @"
<Field Type="Choice"
       DisplayName="Status na-actie"
       Name="StatusNaActie"
       Format="Dropdown"
       FillInChoice="FALSE">
  <CHOICES>
    <CHOICE>Pending</CHOICE>
    <CHOICE>Patiënt gecontacteerd - wacht op respons</CHOICE>
    <CHOICE>Afgehandeld</CHOICE>
  </CHOICES>
</Field>
"@ -ErrorAction SilentlyContinue

# 9. Datum van afhandeling (Date)
Write-Host "Adding column: Datum van afhandeling..." -ForegroundColor Cyan
Add-PnPField -List $ListName -DisplayName "Datum van afhandeling" -InternalName "DatumAfhandeling" -Type DateTime -ErrorAction SilentlyContinue

# 10. Info doorverwijzing (Multi-line text — for external referrals)
Write-Host "Adding column: Info doorverwijzing..." -ForegroundColor Cyan
Add-PnPField -List $ListName -DisplayName "Info doorverwijzing" -InternalName "InfoDoorverwijzing" -Type Note -ErrorAction SilentlyContinue

# 11. Datum doorverwijzing (Date — separate date for external referrals)
Write-Host "Adding column: Datum doorverwijzing..." -ForegroundColor Cyan
Add-PnPField -List $ListName -DisplayName "Datum doorverwijzing" -InternalName "DatumDoorverwijzing" -Type DateTime -ErrorAction SilentlyContinue

# ============================================================
# COLUMN FORMATTING — Color codes for Status na-actie
# ============================================================
Write-Host "`nApplying color formatting to 'Status na-actie'..." -ForegroundColor Cyan

$statusFormatJson = @'
{
  "$schema": "https://developer.microsoft.com/json-schemas/sp/v2/column-formatting.schema.json",
  "elmType": "div",
  "style": {
    "padding": "4px 8px",
    "border-radius": "16px",
    "display": "inline-block",
    "font-size": "13px",
    "font-weight": "600"
  },
  "attributes": {
    "class": {
      "operator": ":",
      "operands": [
        {
          "operator": "==",
          "operands": ["@currentField", "Pending"]
        },
        "sp-css-backgroundColor-warning sp-field-fontSizeSmall",
        {
          "operator": ":",
          "operands": [
            {
              "operator": "==",
              "operands": ["@currentField", "Patiënt gecontacteerd - wacht op respons"]
            },
            "sp-css-backgroundColor-blockingBackground50 sp-field-fontSizeSmall",
            "sp-css-backgroundColor-success sp-field-fontSizeSmall"
          ]
        }
      ]
    }
  },
  "txtContent": "@currentField"
}
'@

Set-PnPField -List $ListName -Identity "StatusNaActie" -Values @{
    CustomFormatter = $statusFormatJson
} -ErrorAction SilentlyContinue

# ============================================================
# DEFAULT VIEW — add all columns in logical order
# ============================================================
Write-Host "`nConfiguring default view..." -ForegroundColor Cyan

$viewFields = @(
    "Naam",
    "Adrema",
    "Aanvrager",
    "InOpvolgingVoor",
    "SoortAanmelding",
    "FormuleerHulpvraag",
    "NaActie",
    "StatusNaActie",
    "DatumAfhandeling",
    "InfoDoorverwijzing",
    "DatumDoorverwijzing"
)

$defaultView = Get-PnPView -List $ListName -Identity "All Items" -ErrorAction SilentlyContinue
if ($defaultView) {
    Set-PnPView -List $ListName -Identity "All Items" -Fields $viewFields
    Write-Host "Default view updated." -ForegroundColor Green
}

Write-Host "`n============================================" -ForegroundColor Green
Write-Host " List '$ListName' is ready!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host @"

Columns created:
  1. Naam                    (Text - renamed Title)
  2. Adrema                  (Text)
  3. Aanvrager               (Text)
  4. In opvolging voor       (Choice: PrEP / Hiv)
  5. Soort aanmelding        (Choice: Nieuwe aanmelding / Gekende patient)
  6. Formuleer hulpvraag     (Multi-line text)
  7. Na-actie                (Choice: 5 options)
  8. Status na-actie         (Choice with color coding)
  9. Datum van afhandeling   (Date)
  10. Info doorverwijzing    (Multi-line text - for external referrals)
  11. Datum doorverwijzing   (Date - for external referrals)

Color codes for 'Status na-actie':
  - Yellow  = Pending
  - Orange  = Patient gecontacteerd - wacht op respons
  - Green   = Afgehandeld
"@
