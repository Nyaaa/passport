from .models import Set
from django.db.models import Prefetch
from django.db import connection

from timeit import default_timer as timer
from django.db import connection, reset_queries


def django_query_analyze(func):
    """decorator to perform analysis on Django queries"""

    def wrapper(*args, **kwargs):
        avs = []
        query_counts = []
        for _ in range(20):
            reset_queries()
            start = timer()
            func(*args, **kwargs)
            end = timer()
            avs.append(end - start)
            query_counts.append(len(connection.queries))
            reset_queries()

        print()
        print(f"ran function {func.__name__}")
        print(f"-" * 20)
        print(f"number of queries: {int(sum(query_counts) / len(query_counts))}")
        print(f"Time of execution: {float(format(min(avs), '.5f'))}s")
        print()
        return func(*args, **kwargs)

    return wrapper


@django_query_analyze
def get_sets_and_orders():
    result = []
    result = Set.objects.raw('''SELECT ms.serial, ms.comment, ms.article_id, mo.date, mo.document, mc.name, md.name, mr.name
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
	ON mo.recipient_id = mr.id''')

    for p in result:
        print(p)
    return result


# selectors.get_sets_and_orders()
# importlib.reload(selectors)

@django_query_analyze
def use_raw_query():
    query = """SELECT ms.serial, ms.comment, ms.article_id, mo.date, mo.document, mc.name, md.name, mr.name
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
    ON mo.recipient_id = mr.id"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows
