import uuid
import pandas as pd
import polars as pl


def generate_content_uuid(ignore_cols: list[str], **kwargs):
    combined_str = "".join(
        [str(value) for key, value in kwargs.items() if key not in ignore_cols]
    )
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, combined_str))


def does_content_uuid_exist(session, orm_object, content_uuid):
    """Checks if a given content_uuid already exists in the database."""
    return (
        session.query(orm_object.content_uuid)
        .filter_by(content_uuid=content_uuid)
        .first()
        is not None
    )


def fetch_proj_player_points_by_date_range(
    date: str, days: int, db_uri
) -> pl.DataFrame:
    """Fetch data from database based on a given date and days range and
    return as Polars DataFrame."""
    # Calculate the end_date based on the given date and days
    end_date = pd.Timestamp(date) + pd.Timedelta(days=days)

    query = f"""
    SELECT * 
    FROM proj_player_points 
    WHERE date >= '{date}' AND date <= '{end_date.strftime('%Y-%m-%d')}'
    """

    try:
        return pl.read_database_uri(query, db_uri)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def filter_df_by_date_range(
    df: pl.DataFrame, date_col: str, start_date: str, days: int
) -> pl.DataFrame:
    """Filter a Polars DataFrame based on a given date and days range."""

    # Convert start_date to a pandas Timestamp object
    start_date_pd = pd.Timestamp(start_date)

    # Calculate end date using the Timestamp object
    end_date_pd = start_date_pd + pd.Timedelta(days=days)

    # Filter dataframe
    filtered_df = df.filter(
        (df[date_col] >= start_date_pd) & (df[date_col] <= end_date_pd)
    )

    return filtered_df


def fetch_data(query: str, db_uri: str, params=None) -> pl.DataFrame:
    """Fetch data from database and return as Polars DataFrame."""
    try:
        return pl.read_database_uri(query.format(params), db_uri)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def write_data(df: pl.DataFrame, table_name, db_uri, if_exists="replace"):
    df_pd = df.to_pandas(use_pyarrow_extension_array=True)
    # Convert datetime columns to handle SQL error
    for col in df_pd.columns:
        if col in ["date", "start_date", "end_date"]:
            df_pd[col] = df_pd[col].astype("datetime64[ns]")
    df_pd.to_sql(table_name, db_uri, if_exists=if_exists, index=False)
