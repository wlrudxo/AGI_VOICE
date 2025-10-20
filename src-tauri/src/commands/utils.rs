// Shared utility functions for commands

use chrono::{NaiveDate, NaiveDateTime};

/// Parse date string in YYYY-MM-DD format
pub fn parse_date(date_str: &str) -> Result<NaiveDate, String> {
    NaiveDate::parse_from_str(date_str, "%Y-%m-%d")
        .map_err(|e| format!("Invalid date format: {}", e))
}

/// Convert NaiveDate to string (YYYY-MM-DD)
pub fn to_date_string(date: &NaiveDate) -> String {
    date.to_string()
}

/// Convert NaiveDateTime to string
pub fn to_datetime_string(datetime: &NaiveDateTime) -> String {
    datetime.to_string()
}
