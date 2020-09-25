import os
from datetime import datetime as dt

import PySimpleGUI as sg
import numpy as np
import pandas as pd
import psycopg2

sql_paws = """Select
        fpo.asin
        ,dp.start_datetime
        ,dp.end_datetime
        ,SUM(fpo.units) as Promo_Units
        ,SUM(fpo.promotional_ops) as Promo_OPS
        ,SUM(fpo.original_ops) as O_OPS
        ,dp.paws_promotion_id

        from edw_local.dim_promotion dp
        LEFT JOIN edw_local.fact_promotion_orders fpo
        ON dp.promotion_key=fpo.promotion_key
        and fpo.region_id = 1
        and fpo.marketplace_key = 1
        and fpo.order_item_level_condition != 6
        where dp.paws_promotion_id = ANY(%s)
        and dp.marketplace_key = 1
        and dp.region_id = 1

        GROUP BY
        fpo.asin
        ,dp.paws_promotion_id
        ,dp.start_datetime
        ,dp.end_datetime;"""

sql_asins = """Select
fpo.asin
,dp.start_datetime
,dp.end_datetime
,SUM(fpo.units) as Promo_Units
,SUM(fpo.promotional_ops) as Promo_OPS
,dp.paws_promotion_id
,dp.promotion_type
from edw_local.dim_promotion dp
LEFT JOIN edw_local.fact_promotion_orders fpo
ON dp.promotion_key=fpo.promotion_key
AND dp.marketplace_key=fpo.marketplace_key
and dp.region_id=fpo.region_id
and fpo.order_item_level_condition != 6
where fpo.asin = ANY(%s)
    and start_datetime between TO_DATE(%s,'YYYYMMDD') and TO_DATE(%s,'YYYYMMDD')
    and dp.promotion_type not in ('Coupon')
and dp.marketplace_key = 1
and dp.region_id = 1

GROUP BY
fpo.asin
,dp.paws_promotion_id
,dp.start_datetime
,dp.end_datetime
,dp.promotion_type;"""

sql_vendors = """Select
fpo.asin
,svs.asin_vendor_code
,dp.start_datetime
,dp.end_datetime
,SUM(fpo.units) as Promo_Units
,SUM(fpo.promotional_ops) as Promo_OPS
,dp.paws_promotion_id
,dp.promotion_type
from edw_local.dim_promotion dp
LEFT JOIN edw_local.fact_promotion_orders fpo
ON dp.promotion_key=fpo.promotion_key
AND dp.marketplace_key=fpo.marketplace_key
and dp.region_id=fpo.region_id
and fpo.order_item_level_condition != 6
Join avs_ws.svs_asins_all svs
on fpo.asin=svs.asin
where svs.asin_vendor_code = ANY(%s)
and start_datetime between TO_DATE(%s,'YYYYMMDD') and TO_DATE(%s,'YYYYMMDD')
and dp.promotion_type not in ('Coupon')
and dp.marketplace_key = 1
and dp.region_id = 1

GROUP BY
svs.asin_vendor_code
,fpo.asin
,dp.paws_promotion_id
,dp.start_datetime
,dp.end_datetime
,dp.promotion_type;"""


def create_connection():
    try:
        con = psycopg2.connect(
            "dbname=rsbidw host=rsbi-analytics.clszsz7jap6y.us-east-1.redshift.amazonaws.com port=8192 user="
            + "akmarmu_ro"
            + " password="
            + "Gemalto@123"
        )
    except TypeError:
        return "typeError"
    except psycopg2.OperationalError:
        return "conError"
    return con


def saving_and_closing_connection(con, cursor):
    result_df = pd.DataFrame(np.array(cursor.fetchall()))
    try:
        result_df.columns = [i[0] for i in cursor.description]
    except ValueError:
        return "valueError"
    cursor.close()
    con.commit()
    con.close()
    return result_df


def saving_file(df, type_):
    username = os.getlogin()
    parent_dir = "C:\\Users\\" + username + "\\Desktop"
    filepath = os.path.join(parent_dir, "DealsSalesReport")

    try:
        os.mkdir(filepath)
    except OSError:
        pass
    df.to_csv(
        filepath
        + "\\"
        + type_
        + "_report_"
        + dt.now().strftime("%d-%m-%Y-%H-%M-%S")
        + ".csv",
        index=False,
    )


def paws_result(paws_ids):
    paws_ids = paws_ids.replace(" ", "")
    paws_ids = paws_ids.split(",")
    try:
        paws_ids = list(set(map(int, paws_ids)))
    except ValueError:
        return "paws ids can be only integers"

    con = create_connection()

    if con == "typeError":
        return "os.environment variable is wrong"
    elif con == "conError":
        return "Connection Problem"
    else:
        cursor = con.cursor()

    cursor.execute(sql_paws, (paws_ids,))

    result_df = saving_and_closing_connection(con, cursor)

    try:
        saving_file(result_df, "paws")
    except AttributeError:
        return "attributeError"

    return "report saved"


def asins_result(asins, start_date, end_date):
    asins = asins.replace(" ", "").replace("\n", "")
    asins = asins.split(",")
    con = create_connection()
    if con == "typeError":
        return "os.environment variable is wrong"
    elif con == "conError":
        return "Connection Problem"
    else:
        cursor = con.cursor()

    cursor.execute(sql_asins, (asins, start_date, end_date))
    result_df = saving_and_closing_connection(con, cursor)

    try:
        saving_file(result_df, "asins")
    except AttributeError:
        return "attributeError"

    return "report saved"


def vendors_result(vendor_codes, start_date, end_date):
    vendor_codes = vendor_codes.replace(" ", "").replace("\n", "")
    vendor_codes = vendor_codes.split(",")
    con = create_connection()
    if con == "typeError":
        return "os.environment variable is wrong"
    elif con == "conError":
        return "Connection Problem"
    else:
        cursor = con.cursor()

    cursor.execute(sql_vendors, (vendor_codes, start_date, end_date))
    result_df = saving_and_closing_connection(con, cursor)

    try:
        saving_file(result_df, "VendorCodes")
    except AttributeError:
        return "attributeError"

    return "report saved"


sg.theme("LightBrown3")

layout = [
    [
        sg.Text(
            "This app will get deals sales by paws ID, ASIN or Vendor Code",
            size=(50, 1),
            justification="center",
            font=("Helvetica", 14),
            relief=sg.RELIEF_RIDGE,
        )
    ],
    [sg.Txt("*" * 110)],
    [sg.Text("Using paws ids:", size=(20, 1), font=("Helvetica", 12))],
    [
        sg.Text("Paws ID         "),
        sg.InputText(
            key="paws", default_text="You can enter multiple paws IDs using comma"
        ),
        sg.Button("Get sales report using Paws ID", key="paws_id"),
    ],
    [sg.Txt("*" * 110)],
    [sg.Text("Using ASINs:", size=(20, 1), font=("Helvetica", 12))],
    [
        sg.Text("ASIN               "),
        sg.InputText(
            key="asins", default_text="You can enter multiple ASINs using comma"
        ),
        sg.Button("Get sales report using ASINs", key="asin"),
    ],
    [sg.Txt("*" * 110)],
    [sg.Text("Using Vendor Codes:", size=(20, 1), font=("Helvetica", 12))],
    [
        sg.Text("Vendor Code    "),
        sg.InputText(
            key="in_vend_code",
            default_text="You can enter multiple vendor codes using comma",
        ),
        sg.Button("Get sales report using Vendor Codes", key="vendor_code"),
    ],
    [sg.Txt("*" * 110)],
    [
        sg.Text("Deal Start Date(YYYYMMDD)"),
        sg.In("", size=(20, 1), key="start_date"),
        sg.CalendarButton(
            "Select Start Date", format="%Y%m%d", target="start_date", key="start_date"
        ),
    ],
    [
        sg.Text("Deal End Date(YYYYMMDD) "),
        sg.In("", size=(20, 1), key="end_date"),
        sg.CalendarButton(
            "Select End Date", format="%Y%m%d", target="end_date", key="end_date"
        ),
    ],
    [
        sg.Cancel("Exit", button_color=("white", "firebrick3")),
        sg.Button("Clear the values", button_color=("white", "firebrick3")),
    ],
    [sg.Text("\t\t\t\t\t\tcontact @vgneam for help/updates")],
]

# Create the Window
window = sg.Window("Deal Sales Report", layout)

# Event Loop to process "events"
while True:
    event, values = window.read()
    if event == "Exit" or event is None:
        sg.popup_timed("Exiting", auto_close_duration=0.2)
        break  # exit button clicked
    elif event == "asin":
        if (
            values["asins"] == "You can enter multiple ASINs using comma"
            or values["asins"] == ""
            or values["start_date"] == ""
            or values["end_date"] == ""
            or values["end_date"] < values["start_date"]
        ):
            sg.popup_error(
                "You need to enter asins, start date and end date and make sure end date is not less than start date"
            )
        else:
            asins_returned = asins_result(
                values["asins"], values["start_date"], values["end_date"]
            )
            if asins_returned == "Connection Problem":
                err_remarks1 = (
                    "Connection problem. Verify if you are in Amazon network.\n"
                )
                err_remarks2 = (
                    "Otherwise user or password to connect with RSBI is wrong"
                )
                sg.popup(err_remarks1 + err_remarks2)
            elif asins_returned == "os.environment variable is wrong":
                sg.popup("environment variables are wrong")
            elif asins_returned == "attributeError":
                sg.popup(
                    "Connection established but received no result.\n"
                    + "Either inputs are wrong or there is no sale for given asins for the period mentioned"
                )
            else:
                sg.popup("file saved in Desktop\\DealsSalesReport")
    elif event == "paws_id":
        if (
            values["paws"] == "You can enter multiple paws IDs using comma"
            or values["paws"] == ""
        ):
            sg.popup_error("You need to enter paws IDs")
        else:
            paws_returned = paws_result(values["paws"])
            if paws_returned == "Connection Problem":
                err_remarks1 = (
                    "Connection problem. Verify if you are in Amazon network.\n"
                )
                err_remarks2 = (
                    "Otherwise user or password to connect with RSBI is wrong"
                )
                sg.popup(err_remarks1 + err_remarks2)
            elif paws_returned == "os.environment variable is wrong":
                sg.popup("paws_returned")
            elif paws_returned == "paws ids can be only integers":
                sg.popup(paws_returned)
            elif paws_returned == "attributeError":
                sg.popup(
                    "Connection established but received no result.\n"
                    + "Either inputs are wrong or there is no sale for given paws ids"
                )
            else:
                sg.popup("file saved in Desktop\\DealsSalesReport")

    elif event == "vendor_code":
        if (
            values["in_vend_code"] == "You can enter multiple ASINs using comma"
            or values["in_vend_code"] == ""
            or values["start_date"] == ""
            or values["end_date"] == ""
            or values["end_date"] < values["start_date"]
        ):
            sg.popup_error(
                "You need to enter vendor codes, start date & end date and end date should be greater than start date"
            )
        else:
            vendors_returned = vendors_result(
                values["in_vend_code"], values["start_date"], values["end_date"]
            )
            if vendors_returned == "Connection Problem":
                err_remarks1 = (
                    "Connection problem. Verify if you are in Amazon network.\n"
                )
                err_remarks2 = (
                    "Otherwise user or password to connect with RSBI is wrong"
                )
                sg.popup(err_remarks1 + err_remarks2)
            elif vendors_returned == "os.environment variable is wrong":
                sg.popup("environment variables are wrong")
            elif vendors_returned == "attributeError":
                sg.popup(
                    "Connection established but received no result.\n"
                    + "Either inputs are wrong or there is no sale for given asins for the period mentioned"
                )
            else:
                sg.popup("file saved in Desktop\\DealsSalesReport")
    elif event == "Clear the values":
        window["paws"].update("")
        window["asins"].update("")
        window["in_vend_code"].update("")
        window["start_date"].update("")
        window["end_date"].update("")
    else:
        sg.popup_error("Issue")

window.close()
