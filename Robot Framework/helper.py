import pandas as pd
import pyarrow.parquet as pq
import os
from bs4 import BeautifulSoup

def extract_html_table_data(html_source, table_selector=None):
    """Extracts HTML table data from the browser source or falls back to SVG extraction."""
    if not html_source:
        raise ValueError("HTML source must be provided.")

    soup = BeautifulSoup(html_source, "html.parser")
    table = None
    if table_selector:
        selector = table_selector.strip()
        if selector.startswith("css="):
            selector = selector[4:]
            table = soup.select_one(selector)
        elif selector.startswith("css:"):
            selector = selector[4:]
            table = soup.select_one(selector)
        elif selector.startswith("xpath="):
            table = None
        else:
            table = soup.select_one(selector)

    if table is None:
        table = soup.find("table")

    if table:
        headers = []
        header_row = table.find("thead")
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
        if not headers:
            first_row = table.find("tr")
            if first_row:
                headers = [cell.get_text(strip=True) for cell in first_row.find_all(["th", "td"])]

        rows = []
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            row_values = [cell.get_text(strip=True) for cell in cells]
            if row_values and any(value != "" for value in row_values):
                rows.append(row_values)

        if headers and rows and rows[0] == headers:
            rows = rows[1:]

        if headers:
            return pd.DataFrame(rows, columns=headers)
        return pd.DataFrame(rows)

    return extract_svg_table_from_browser(html_source)

def extract_svg_table_from_browser(html_source):
    """Extracts table-like data from Plotly-rendered SVG elements."""
    soup = BeautifulSoup(html_source, "html.parser")
    table_group = soup.find("g", {"class": "table"})
    if table_group:
        columns = table_group.find_all("g", {"class": "y-column"})
        if columns:
            col_values = []
            for col in columns:
                texts = [t.get_text(strip=True) for t in col.find_all("text")]
                texts = [t for t in texts if t]
                if texts:
                    col_values.append(texts)

            if col_values and all(len(col_values[0]) == len(cv) for cv in col_values):
                headers = [cv[-1] for cv in col_values]
                rows = [tuple(cv[i] for cv in col_values) for i in range(len(col_values[0]) - 1)]
                if headers and rows:
                    return pd.DataFrame(rows, columns=headers)

    svgs = soup.find_all("svg")
    if not svgs:
        raise ValueError("No SVG found in the rendered HTML.")

    svg = max(svgs, key=lambda s: len(s.find_all("text")))
    texts = []
    for t in svg.find_all("text"):
        txt = t.get_text(strip=True)
        if not txt:
            continue
        try:
            x = float(t.get("x", 0))
        except (TypeError, ValueError):
            x = 0.0
        try:
            y = float(t.get("y", 0))
        except (TypeError, ValueError):
            y = 0.0
        texts.append((round(y, 1), x, txt))

    import collections
    from operator import itemgetter

    rows = collections.defaultdict(list)
    for y, x, val in texts:
        rows[y].append((x, val))

    sorted_rows = sorted(rows.items())
    matrix = []
    for _, row in sorted_rows:
        row_sorted = [v for x, v in sorted(row, key=itemgetter(0))]
        matrix.append(row_sorted)

    if len(matrix) < 2:
        raise ValueError("Unable to parse enough SVG rows to build a DataFrame.")

    return pd.DataFrame(matrix[1:], columns=matrix[0])

def read_filtered_parquet(folder_path, filter_date):
    """Reads Parquet files from a folder and applies optional date filtering."""
    folder_path = os.path.normpath(folder_path)
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Parquet folder path does not exist: {folder_path}")

    if os.path.isdir(folder_path):
        try:
            import pyarrow.dataset as ds
        except ModuleNotFoundError as e:
            raise ImportError("pyarrow is required to read partitioned Parquet datasets.") from e
        dataset = ds.dataset(folder_path, format="parquet", partitioning="hive")
        df = dataset.to_table().to_pandas()
    else:
        df = pq.read_table(folder_path).to_pandas()

    if filter_date and not df.empty:
        date_columns = [
            c for c in df.columns
            if isinstance(c, str) and c.lower() in [
                "date", "dt", "report_date", "visit_date", "partition_date"
            ]
        ]
        if date_columns:
            df = df[df[date_columns[0]].astype(str) == filter_date]
        else:
            partition_values = []
            for root, dirs, files in os.walk(folder_path):
                relative = os.path.relpath(root, folder_path)
                for part in relative.replace("\\", "/").split("/"):
                    if "=" in part:
                        key, value = part.split("=", 1)
                        if key.lower() in ["date", "dt", "report_date", "visit_date", "partition_date"]:
                            partition_values.append((key, value))
            if partition_values:
                key, value = partition_values[0]
                if value == filter_date:
                    df[key] = value
                else:
                    df = df[df.get(key, df.columns[0]).astype(str) == filter_date]
            else:
                raise ValueError("No date column found to apply the filter.")

    return df

def compare_dataframes(df1, df2, filter_date=None):
    """Compares two DataFrames and returns a match boolean plus diff string.

    If `filter_date` (string) is provided, the same filter will be applied to
    both DataFrames before comparison. The filter looks for common date-like
    column names first and then falls back to substring matching across
    columns.
    """
    if df1 is None or df2 is None:
        return False, "One of the DataFrames is None."

    def _filter_df_by_date(df, filter_date):
        if not filter_date or df is None or df.empty:
            return df
        candidates = [
            c for c in df.columns
            if isinstance(c, str) and c.lower() in [
                "date", "dt", "report_date", "visit_date", "partition_date"
            ]
        ]
        if candidates:
            col = candidates[0]
            try:
                return df[df[col].astype(str) == filter_date]
            except Exception:
                mask = df[col].astype(str).str.contains(filter_date, na=False)
                return df[mask]

        # Try value substring matching across columns
        for col in df.columns:
            try:
                series = df[col].astype(str)
                if series.str.contains(filter_date, na=False).any():
                    return df[series.str.contains(filter_date, na=False)]
            except Exception:
                continue

        # Nothing matched; return original
        return df

    if filter_date:
        df1 = _filter_df_by_date(df1, filter_date)
        df2 = _filter_df_by_date(df2, filter_date)

    try:
        pd.testing.assert_frame_equal(
            df1.reset_index(drop=True),
            df2.reset_index(drop=True),
            check_dtype=False,
            check_like=True,
        )
        return True, ""
    except AssertionError as exc:
        diff_parts = []
        if df1.shape != df2.shape:
            diff_parts.append(f"Shape mismatch: report={df1.shape}, parquet={df2.shape}")

        try:
            left_only = pd.concat([df1, df2, df2]).drop_duplicates(keep=False)
        except Exception:
            left_only = pd.DataFrame()
        try:
            right_only = pd.concat([df2, df1, df1]).drop_duplicates(keep=False)
        except Exception:
            right_only = pd.DataFrame()

        if not left_only.empty:
            diff_parts.append("Rows in report not in parquet:\n" + left_only.to_string(index=False))
        if not right_only.empty:
            diff_parts.append("Rows in parquet not in report:\n" + right_only.to_string(index=False))
        diff_parts.append(str(exc))
        return False, "\n\n".join(diff_parts)



