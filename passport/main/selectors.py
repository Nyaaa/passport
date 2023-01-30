from .models import Set
from django.db.models import Prefetch


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
    sets = Set.objects.all().prefetch_related("order_set")[:10]
    for myset in sets:
        order = myset.order_set.all().filter(sets=myset).order_by('date').last()
        date = order.date if order else None
        distributor = order.distributor if order else None
        recipient = order.recipient if order else None
        document = order.document if order else None
        city = order.city if order else None

        result.append(
            {
                "serial": myset.serial,
                "article": myset.article,
                "comment": myset.comment,
                "date": date,
                "distributor": distributor,
                "recipient": recipient,
                "document": document,
                "city": city,
            }
        )
    return result

# selectors.get_sets_and_orders()
# importlib.reload(selectors)

