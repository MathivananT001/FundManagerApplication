"""Tests for report service Lambda handlers."""
from unittest.mock import patch, MagicMock
import json


@patch("handler.s3")
@patch("handler._fetch_json")
def test_generate_group_summary_pdf(mock_fetch, mock_s3):
    mock_fetch.return_value = {
        "name": "Test Fund", "member_count": 5, "member_slots": 10,
        "targeting_amount": 50000, "monthly_auction_amount": 5000,
        "manager_fee_percent": 2, "status": "ACTIVE",
    }
    mock_s3.put_object.return_value = {}
    mock_s3.generate_presigned_url.return_value = "https://s3.presigned/report.pdf"

    from handler import generate_group_summary_report
    result = generate_group_summary_report({"group_id": "grp-001", "format": "pdf"}, None)
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "download_url" in body


@patch("handler.s3")
@patch("handler._fetch_json")
def test_generate_group_summary_excel(mock_fetch, mock_s3):
    mock_fetch.return_value = {
        "name": "Test Fund", "member_count": 5, "member_slots": 10,
        "targeting_amount": 50000, "monthly_auction_amount": 5000,
        "manager_fee_percent": 2, "status": "ACTIVE",
    }
    mock_s3.put_object.return_value = {}
    mock_s3.generate_presigned_url.return_value = "https://s3.presigned/report.xlsx"

    from handler import generate_group_summary_report
    result = generate_group_summary_report({"group_id": "grp-001", "format": "excel"}, None)
    assert result["statusCode"] == 200


@patch("handler.s3")
@patch("handler._fetch_json")
def test_generate_auction_history(mock_fetch, mock_s3):
    mock_fetch.return_value = [
        {"month_number": 1, "status": "CLOSED", "winner_id": "user-002",
         "winning_bid_amount": 1500, "disbursement_amount": 3400},
    ]
    mock_s3.put_object.return_value = {}
    mock_s3.generate_presigned_url.return_value = "https://s3.presigned/auction.pdf"

    from handler import generate_auction_history_report
    result = generate_auction_history_report({"group_id": "grp-001", "format": "pdf"}, None)
    assert result["statusCode"] == 200
