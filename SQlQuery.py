import psycopg2
import numpy as np
import pandas as pd

con = psycopg2.connect(
    "dbname=rsbidw host=rsbi-analytics.clszsz7jap6y.us-east-1.redshift.amazonaws.com port=8192 user=akmarmu_ro password=Sandheek@987"
)


cursor = con.cursor()
cursor.execute(
    """  select tbl1.run_date,
tbl1.product_group_name, 
tbl1.svs_product_family,
tbl1.vendor_code,
tbl1.svs_primary_vendor_code,
tbl1.case_id, 
tbl2.case_id_short,
tbl1.activity,
tbl5.initial_task_type,
tbl2.is_activity_changed,
tbl2.task_classification, 
tbl1.ticket_status,
tbl1.requester_email,
tbl1.requester_name,
tbl1.requester_business_title, 
tbl2.is_expedited, 
tbl2.arrived_datetime, 
tbl2.original_due_date, 
tbl2.sla_datetime,
tbl2.max_resolved_datetime,
tbl2.max_closed_datetime, 
tbl2.max_escalated_datetime, 
tbl2.is_rbsfe_flipped,
tbl2.first_flipped_to_rbsfe,
tbl2.first_flipped_from_rbsfe,
tbl1.met_sla, 
tbl2.sla_miss_reason, 
tbl1.completed_correctly_first_time, 
tbl1.ftr_miss_bucket, 
tbl2.ever_functional_expert, 
tbl2.ever_escalated, 
tbl2.last_closed_reason_code, 
tbl2.closed_reason_code_breakdown,
tbl2.num_comments_fe, 
tbl2.num_comments_other, 
tbl2.num_comments_rbs, 
tbl2.num_comments_retail



from avs_ws.avs_wbr_case_level tbl1
left outer join avs_ws.case_level_platform_addons tbl2 on tbl1.case_id = tbl2.case_id
left outer join avs_ws.svs_agreements tbl3 on tbl1.product_group_name = tbl3.product_group_name
left outer join avs_ws.vs_activities tbl4 on tbl1.activity = tbl4.activity_name_platform
left outer join avs_ws.winston_tasks_activity_changes tbl5 on tbl1.case_id = tbl5.task_id
where tbl1.region_id = 'AVS'
and tbl2.task_classification in ('Reactive')
group by tbl1.run_date,
tbl1.product_group_name, 
tbl1.svs_product_family,
tbl1.vendor_code,
tbl1.svs_primary_vendor_code,
tbl1.case_id, 
tbl2.case_id_short,
tbl1.activity,
tbl5.initial_task_type,
tbl2.is_activity_changed,
tbl2.task_classification, 
tbl1.ticket_status,
tbl1.requester_email,
tbl1.requester_name,
tbl1.requester_business_title, 
tbl2.is_expedited, 
tbl2.arrived_datetime, 
tbl2.original_due_date, 
tbl2.sla_datetime,
tbl2.max_resolved_datetime,
tbl2.max_closed_datetime, 
tbl2.max_escalated_datetime, 
tbl2.is_rbsfe_flipped,
tbl2.first_flipped_to_rbsfe,
tbl2.first_flipped_from_rbsfe,
tbl1.met_sla, 
tbl2.sla_miss_reason, 
tbl1.completed_correctly_first_time, 
tbl1.ftr_miss_bucket, 
tbl2.ever_functional_expert, 
tbl2.ever_escalated, 
tbl2.last_closed_reason_code, 
tbl2.closed_reason_code_breakdown,
tbl2.num_comments_fe, 
tbl2.num_comments_other, 
tbl2.num_comments_rbs, 
tbl2.num_comments_retail

  """
)
result_df = pd.DataFrame(np.array(cursor.fetchall()))
result_df.columns = [i[0] for i in cursor.description]
cursor.close()
con.commit()
con.close()
