from django.db import connection


def use_raw_query():
    """No LIMIT"""
    query = """SELECT 
    ms.serial, 
    ms.comment, 
    ms.article_id AS article, 
    max(mo.date) AS date,
    mo.document,
    mc.name AS city,
    md.name AS distributor,
    mr.name AS recipient
FROM main_set ms
LEFT OUTER JOIN main_order_sets mos
    ON ms.serial = mos.set_id
LEFT OUTER JOIN main_order mo
    ON mos.order_id = mo.id
LEFT OUTER JOIN main_city mc
    ON mo.city_id = mc.id
LEFT OUTER JOIN main_distributor md
    ON mo.distributor_id =md.id
LEFT OUTER JOIN main_recipient mr
    ON mo.recipient_id = mr.id
GROUP BY ms.serial"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [dict(zip(column_names, row))
            for row in rows]
    return data
