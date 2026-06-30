import pandas as pd
import numpy as np
from yahooquery import Ticker
import requests
import os



def fetch_all_bist_tickers():
    """
    Dynamically pulls the live list of all companies trading on Borsa Istanbul (BIST)
    via public market feeds to guarantee full market coverage.
    """
    # doesnt work anymore didnt find any just taken them once update them when u wanna see new things fast using regex or IDE tricks.
    """
    print("Fetching active BIST ticker database...")
    try:
        url = "https://raw.githubusercontent.com/atb-isi/bist30-tickers/main/bist_all.txt"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            tickers = [line.strip() for line in response.text.split('\n') if line.strip()]
            return [f"{t}.IS" if not t.endswith(".IS") else t for t in tickers]
    except Exception as e:
        print(f"Dynamic fetch fallback initiated due to: {e}")
    """
    # Core structural anchors fallback list
    fallback = ["A1CAP","A1YEN","AAGYO","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON","AGESA","AGHOL","AGROT","AGYO","AHGAZ","AHSGY","AKBNK","AKCNS","AKENR","AKFGY","AKFIS","AKFYE","AKGRT","AKHAN","AKMGY","AKSA","AKSEN","AKSGY","AKSUE","AKYHO","ALARK","ALBRK","ALCAR","ALCTL","ALFAS","ALGYO","ALKA","ALKIM","ALKLC","ALTNY","ALVES","ANELE","ANGEN","ANHYT","ANSGR","ARASE","ARCLK","ARDYZ","ARENA","ARFYE","ARMGD","ARSAN","ARTMS","ARZUM","ASELS","ASGYO","ASTOR","ASUZU","ATAGY","ATAKP","ATATP","ATATR","ATEKS","ATLAS","ATSYH","AVGYO","AVHOL","AVOD","AVPGY","AVTUR","AYCES","AYDEM","AYEN","AYES","AYGAZ","AZTEK","BAGFS","BAHKM","BAKAB","BALAT","BALSU","BANVT","BARMA","BASCM","BASGZ","BAYRK","BEGYO","BERA","BESLR","BESTE","BEYAZ","BFREN","BIENY","BIGCH","BIGEN","BIGTK","BIMAS","BINBN","BINHO","BIOEN","BIZIM","BJKAS","BLCYT","BLUME","BMSCH","BMSTL","BNTAS","BOBET","BORLS","BORSK","BOSSA","BRISA","BRKO","BRKSN","BRKVY","BRLSM","BRMEN","BRSAN","BRYAT","BSOKE","BTCIM","BUCIM","BULGS","BURCE","BURVA","BVSAN","BYDNR","CANTE","CASA","CATES","CCOLA","CELHA","CEMAS","CEMTS","CEMZY","CEOEM","CGCAM","CIMSA","CLEBI","CMBTN","CMENT","CONSE","COSMO","CRDFA","CRFSA","CUSAN","CVKMD","CWENE","DAGI","DAPGM","DARDL","DCTTR","DENGE","DERHL","DERIM","DESA","DESPC","DEVA","DGATE","DGGYO","DGNMO","DIRIT","DITAS","DMRGD","DMSAS","DNISI","DOAS","DOCO","DOFER","DOFRB","DOGUB","DOHOL","DOKTA","DSTKF","DUNYH","DURDO","DURKN","DYOBY","DZGYO","EBEBK","ECILC","ECOGR","ECZYT","EDATA","EDIP","EFOR","EGEEN","EGEGY","EGEPO","EGGUB","EGPRO","EGSER","EKDMR","EKGYO","EKIZ","EKOS","EKSUN","ELITE","EMKEL","EMNIS","EMPAE","ENDAE","ENERY","ENJSA","ENKAI","ENPRA","ENSRI","ENTRA","EPLAS","ERBOS","ERCB","EREGL","ERSU","ESCAR","ESCOM","ESEN","ETILR","ETYAT","EUHOL","EUKYO","EUPWR","EUREN","EUYO","EYGYO","FADE","FENER","FLAP","FMIZP","FONET","FORMT","FORTE","FRIGO","FRMPL","FROTO","FZLGY","GARAN","GARFA","GATEG","GEDIK","GEDZA","GENIL","GENKM","GENTS","GEREL","GESAN","GIPTA","GLBMD","GLCVY","GLRMK","GLRYH","GLYHO","GMTAS","GOKNR","GOLTS","GOODY","GOZDE","GRNYO","GRSEL","GRTHO","GSDDE","GSDHO","GSRAY","GUBRF","GUNDG","GWIND","GZNMI","HALKB","HATEK","HATSN","HDFGS","HEDEF","HEKTS","HKTM","HLGYO","HOROZ","HRKET","HTTBT","HUBVC","HUNER","HURGZ","ICBCT","ICUGS","IDGYO","IEYHO","IHAAS","IHEVA","IHGZT","IHLAS","IHLGM","IHYAY","IMASM","INDES","INFO","INGRM","INTEK","INTEM","INVEO","INVES","ISATR","ISBIR","ISBTR","ISCTR","ISDMR","ISFIN","ISGSY","ISGYO","ISKPL","ISKUR","ISMEN","ISSEN","ISYAT","IZENR","IZFAS","IZINV","IZMDC","JANTS","KAPLM","KAREL","KARSN","KARTN","KATMR","KAYSE","KBORU","KCAER","KCHOL","KENT","KERVN","KFEIN","KGYO","KIMMR","KLGYO","KLKIM","KLMSN","KLNMA","KLRHO","KLSER","KLSYN","KLYPV","KMPUR","KNFRT","KOCMT","KONKA","KONTR","KONYA","KOPOL","KORDS","KOTON","KRDMA","KRDMB","KRDMD","KRGYO","KRONT","KRPLS","KRSTL","KRTEK","KRVGD","KSTUR","KTLEV","KTSKR","KUTPO","KUVVA","KUYAS","KZBGY","KZGYO","LIDER","LIDFA","LILAK","LINK","LKMNH","LMKDC","LOGO","LRSHO","LUKSK","LXGYO","LYDHO","LYDYE","MAALT","MACKO","MAGEN","MAKIM","MAKTK","MANAS","MARBL","MARKA","MARMR","MARTI","MAVI","MCARD","MEDTR","MEGAP","MEGMT","MEKAG","MEPET","MERCN","MERIT","MERKO","METRO","MEYSU","MGROS","MHRGY","MIATK","MMCAS","MNDRS","MNDTR","MOBTL","MOGAN","MOPAS","MPARK","MRGYO","MRSHL","MSGYO","MTRKS","MTRYO","MZHLD","NATEN","NETAS","NETCD","NIBAS","NTGAZ","NTHOL","NUGYO","NUHCM","OBAMS","OBASE","ODAS","ODINE","OFSYM","ONCSM","ONRYT","ORCAY","ORGE","ORMA","OSMEN","OSTIM","OTKAR","OTTO","OYAKC","OYAYO","OYLUM","OYYAT","OZATD","OZGYO","OZKGY","OZRDN","OZSUB","OZYSR","PAGYO","PAHOL","PAMEL","PAPIL","PARSN","PASEU","PATEK","PCILT","PEKGY","PENGD","PENTA","PETKM","PETUN","PGSUS","PINSU","PKART","PKENT","PLTUR","PNLSN","PNSUT","POLHO","POLTK","PRDGS","PRKAB","PRKME","PRZMA","PSDTC","PSGYO","QNBFK","QNBTR","QUAGR","RALYH","RAYSG","REEDR","RGYAS","RNPOL","RODRG","RTALB","RUBNS","RUZYE","RYGYO","RYSAS","SAFKR","SAHOL","SAMAT","SANEL","SANFM","SANKO","SARKY","SASA","SAYAS","SDTTR","SEGMN","SEGYO","SEKFK","SEKUR","SELEC","SELVA","SERNT","SEYKM","SILVR","SISE","SKBNK","SKTAS","SKYLP","SKYMD","SMART","SMRTG","SMRVA","SNGYO","SNICA","SNPAM","SODSN","SOKE","SOKM","SONME","SRVGY","SUMAS","SUNTK","SURGY","SUWEN","SVGYO","TABGD","TARKM","TATEN","TATGD","TAVHL","TBORG","TCELL","TCKRC","TDGYO","TEHOL","TEKTU","TERA","TEZOL","TGSAS","THYAO","TKFEN","TKNSA","TLMAN","TMPOL","TMSN","TNZTP","TOASO","TRALT","TRCAS","TRENJ","TRGYO","TRHOL","TRILC","TRMET","TSGYO","TSKB","TSPOR","TTKOM","TTRAK","TUCLK","TUKAS","TUPRS","TUREX","TURGG","TURSG","UCAYM","UFUK","ULAS","ULKER","ULUFA","ULUSE","ULUUN","UNLU","USAK","VAKBN","VAKFA","VAKFN","VAKKO","VANGD","VBTYZ","VERTU","VERUS","VESBE","VESTL","VKFYO","VKGYO","VKING","VRGYO","VSNMD","YAPRK","YATAS","YAYLA","YBTAS","YEOTK","YESIL","YGGYO","YIGIT","YKBNK","YKSLN","YONGA","YUNSA","YYAPI","YYLGD","ZEDUR","ZERGY","ZGYO","ZOREN","ZRGYO"]
    # fallback = ["THYAO", "ULKER", "KCHOL"]
    # fallback = ["THYAO", "ULKER", "KCHOL", "ASELS", "BIMAS", "EREGL", "SISE", "GARAN", "AKBNK", "TUPRS", "SAHOL", "ENKAI"]
    return [f"{t}.IS" for t in fallback]

def scan_full_market_for_anomalies():
    # 1. Grab the full universe
    bist_universe = fetch_all_bist_tickers()
    print(f"Successfully loaded {len(bist_universe)} tickers into the live checker.\n")
    
    if len(bist_universe) <= 12:
        print("[CRITICAL ALERT] The script fell back to the 12-ticker backup list!")
        print("Please check your internet connection or run the script again.")
        return

    print("Querying Yahoo internal API endpoints for all stocks...")
    t = Ticker(bist_universe)
    summary = t.summary_detail
    key_stats = t.key_stats
    
    anomaly_set = set()
    print("\n" + "="*20 + " LIVE TRACKING STRINGS DETECTED " + "="*20)
    
    for ticker in bist_universe:
        clean_symbol = ticker.replace(".IS", "")
        t_summary = summary.get(ticker, {}) if isinstance(summary, dict) else {}
        t_stats = key_stats.get(ticker, {}) if isinstance(key_stats, dict) else {}
        
        if isinstance(t_summary, str): t_summary = {}
        if isinstance(t_stats, str): t_stats = {}
        
        # Track every individual field to catch the exact culprit
        checks = {
            "Trailing P/E": t_summary.get("trailingPE"),
            "Forward P/E": t_summary.get("forwardPE"),
            "Price to Book (Summary)": t_summary.get("priceToBook"),
            "Price to Book (Stats)": t_stats.get("priceToBook"),
            "Price to Sales": t_summary.get("priceToSalesTrailing12Months")
        }
        
        for field_name, value in checks.items():
            if value is not None:
                # If it's a string, find out what it is
                if isinstance(value, str):
                    print(f"ALERT -> Stock: {clean_symbol:<6} | Field: {field_name:<23} | Value: '{value}'")
                    anomaly_set.add(value)
                else:
                    # Double check if it fails numeric parsing (e.g. nested objects)
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        print(f"ALERT -> Stock: {clean_symbol:<6} | Field: {field_name:<23} | Unparseable Type: {type(value)}")
                        anomaly_set.add(str(value))

    print("\n" + "="*23 + " METRIC AUDIT RESULTS " + "="*23)
    print(f"Total unique string variations causing crashes: {anomaly_set}")
    print("="*68)

def build_raw_market_dataframe(tickers):
    """
    Executes high-speed bulk JSON calls using yahooquery.
    """
    t = Ticker(tickers)
    summary = t.summary_detail
    key_stats = t.key_stats
    
    raw_records = []
    
    for ticker in tickers:
        clean_symbol = ticker.replace(".IS", "")
        
        t_summary = summary.get(ticker, {}) if isinstance(summary, dict) else {}
        t_stats = key_stats.get(ticker, {}) if isinstance(key_stats, dict) else {}
        if isinstance(t_summary, str): t_summary = {}
        if isinstance(t_stats, str): t_stats = {}
        
        pe_trailing = t_summary.get("trailingPE")
        pe_forward = t_summary.get("forwardPE")
        
        # Blended P/E logic (70% Trailing / 30% Forward)
        if pe_trailing and not isinstance(pe_trailing, str) and pe_trailing > 0:
            blended_pe = (0.7 * pe_trailing) + (0.3 * pe_forward) if (pe_forward and pe_forward > 0) else pe_trailing
        else:
            blended_pe = np.nan
            
        raw_records.append({
            "Ticker": clean_symbol,
            "Trailing_PE": pe_trailing if (pe_trailing and not isinstance(pe_trailing, str) and pe_trailing > 0) else np.nan,
            "Forward_PE": pe_forward if (pe_forward and not isinstance(pe_forward, str) and pe_forward > 0) else np.nan,
            "Blended_PE": blended_pe,
            "Raw_PB": t_stats.get("priceToBook") or t_summary.get("priceToBook") or np.nan,
            "Raw_PS": t_summary.get("priceToSalesTrailing12Months") or np.nan
        })
        
    return pd.DataFrame(raw_records)

def calculate_asymmetric_value_score(df):
    """
    Normalizes metrics using your specific fractions: P/B: 1.0, P/E: 1/8.5, P/S: 1/10.
    Robust type casting prevents strings or NaNs from crashing the 610-ticker run.
    """
    output_df = df.copy()
    
    pe_scale = 1.0 / 8.5
    pb_scale = 1.0
    ps_scale = 1.0 / 10.0
    
    # Force everything to numeric. Any string error or N/A becomes a clean NaN
    output_df['Blended_PE'] = pd.to_numeric(output_df['Blended_PE'], errors='coerce')
    output_df['Raw_PB'] = pd.to_numeric(output_df['Raw_PB'], errors='coerce')
    output_df['Raw_PS'] = pd.to_numeric(output_df['Raw_PS'], errors='coerce')
    
    # Fill missing values or negative numbers with the penalty baselines cleanly
    processed_pe = output_df['Blended_PE'].fillna(100.0).apply(lambda x: x if x > 0 else 100.0)
    processed_pb = output_df['Raw_PB'].fillna(10.0).apply(lambda x: x if x > 0 else 10.0)
    processed_ps = output_df['Raw_PS'].fillna(10.0).apply(lambda x: x if x > 0 else 10.0)
    
    scaled_pe = processed_pe * pe_scale
    scaled_pb = processed_pb * pb_scale
    scaled_ps = processed_ps * ps_scale
    
    core_anchor = np.minimum(scaled_pe, scaled_pb)
    secondary_anchor = np.maximum(scaled_pe, scaled_pb)
    
    output_df['Custom_Value_Score'] = (0.55 * core_anchor) + (0.25 * secondary_anchor) + (0.20 * scaled_ps)
    return output_df

def format_dataframe_to_grouped_string(df):
    """
    Manually creates uniform columns aligned horizontally with explicit '|' dividers.
    """
    lines = []
    header = "Symbol  | Trailing  Forward   Blended  | P/B Ratio  P/S Ratio | Final Value"
    divider = "-" * len(header)
    lines.append(header)
    lines.append(divider)
    
    for _, row in df.iterrows():
        # Type-safe formatter that protects against residual string types
        def fmt(v, prec=2):
            try:
                num = float(v)
                if pd.isna(num) or num == 100.0 or num == 10.0:
                    return "N/A"
                return f"{num:.{prec}f}"
            except (ValueError, TypeError):
                return "N/A"
        
        ticker = f"{str(row['Ticker']):<7}"
        trailing = f"{fmt(row['Trailing_PE']):>9}"
        forward = f"{fmt(row['Forward_PE']):>9}"
        blended = f"{fmt(row['Blended_PE']):>9}"
        pb = f"{fmt(row['Raw_PB']):>10}"
        ps = f"{fmt(row['Raw_PS']):>10}"
        score = f"{fmt(row['Custom_Value_Score'], 4):>12}"
        
        line = f"{ticker} | {trailing} {forward} {blended}  | {pb} {ps} | {score}"
        lines.append(line)
        
    return "\n".join(lines)

def filter_valuation_metrics(df: pd.DataFrame, upper_limits: dict) -> pd.DataFrame:
    """Filters a valuation DataFrame based on maximum upper limits for specific columns.

    Parameters:
    -----------
    df : pd.DataFrame
        The input DataFrame containing financial metrics.
    upper_limits : dict
        A dictionary where keys are column names and values are the maximum
        allowed thresholds (e.g., {'Trailing_PE': 30, 'Raw_PB': 5})

    Returns:
    --------
    pd.DataFrame
        The filtered DataFrame.
    """
    # Create a copy to avoid SettingWithCopyWarning if modifying later
    filtered_df = df.copy()

    # Iterate through the provided filter limits
    for column, max_limit in upper_limits.items():
        if column in filtered_df.columns and max_limit is not None:
            # We keep rows where the value is LESS THAN OR EQUAL to the limit OR is NaN
            # (Adjust the condition if you want to drop NaNs entirely during filtration)
            condition = (filtered_df[column] <= max_limit) | (
                filtered_df[column].isna()
            )
            filtered_df = filtered_df[condition]

    return filtered_df






if not os.path.exists('valuation'):
    os.makedirs('valuation')
# Fetch and compute metrics
bist_universe = fetch_all_bist_tickers()
raw_df = build_raw_market_dataframe(bist_universe)
master_df = calculate_asymmetric_value_score(raw_df)

# Compile the 4 tables with distinct sort configurations
t1 = master_df.sort_values(by="Ticker", ascending=True)
t2 = master_df.sort_values(by="Raw_PB", ascending=True, na_position='last')
t3 = master_df.sort_values(by="Blended_PE", ascending=True, na_position='last')
t3_1 = master_df.sort_values(by="Trailing_PE", ascending=True, na_position='last')
t3_2 = master_df.sort_values(by="Forward_PE", ascending=True, na_position='last')
t4 = master_df.sort_values(by="Custom_Value_Score", ascending=True)

# Write cleanly to file using custom string format function
with open("valuation/bist_alph.txt", "w", encoding="utf-8") as f:
    # Table 1
    f.write("=" * 22 + " TABLE 1: ALPHABETICAL TICKER ORDER " + "=" * 22 + "\n\n")
    f.write(format_dataframe_to_grouped_string(t1))
    f.write("\n\n" + "#" * 80 + "\n\n\n")
with open("valuation/bist_ord_pb.txt", "w", encoding="utf-8") as f:
    # Table 2
    f.write("=" * 20 + " TABLE 2: SORTED BY PRICE-TO-BOOK (P/B) " + "=" * 20 + "\n\n")
    f.write(format_dataframe_to_grouped_string(t2))
    f.write("\n\n" + "#" * 80 + "\n\n\n")
with open("valuation/bist_ord_pe.txt", "w", encoding="utf-8") as f:
    # Table 3 (Sorted by Blended PE right after PB table)
    f.write("=" * 25 + " TABLE 3: SORTED BY BLENDED P/E " + "=" * 25 + "\n\n")
    f.write(format_dataframe_to_grouped_string(t3))
    f.write("\n\n" + "#" * 80 + "\n\n\n")
with open("valuation/bist_ord_pe_trail.txt", "w", encoding="utf-8") as f:
    # Table 3 (Sorted by Blended PE right after PB table)
    f.write("=" * 25 + " TABLE 3_1: SORTED BY trailing P/E " + "=" * 25 + "\n\n")
    f.write(format_dataframe_to_grouped_string(t3_1))
    f.write("\n\n" + "#" * 80 + "\n\n\n")
with open("valuation/bist_ord_pe_forw.txt", "w", encoding="utf-8") as f:
    # Table 3 (Sorted by Blended PE right after PB table)
    f.write("=" * 25 + " TABLE 3_2: SORTED BY forward P/E " + "=" * 25 + "\n\n")
    f.write(format_dataframe_to_grouped_string(t3_2))
    f.write("\n\n" + "#" * 80 + "\n\n\n")
with open("valuation/bist_ord_customval.txt", "w", encoding="utf-8") as f:
    # Table 4
    f.write("=" * 12 + " TABLE 4: SORTED BY CUSTOM ASYMMETRIC VALUE SCORE " + "=" * 12 + "\n\n")
    f.write(format_dataframe_to_grouped_string(t4))
    f.write("\n")
    
print("Market analysis completely exported to valuation_bist.txt with clean pipeline groupings.")
