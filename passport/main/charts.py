import matplotlib.pyplot as plt
from io import StringIO
from .models import Set, Order
from django.db.models import OuterRef, Subquery, Count


def get_data():
    qs = Set.objects.all()
    latest_order = Order.objects.filter(sets=OuterRef('pk')).order_by('-date')[:1]
    qs = qs.prefetch_related('order_set').annotate(recipient=Subquery(latest_order.values('recipient__name')),
                                                   distributor=Subquery(latest_order.values('distributor__name')),
                                                   )
    return qs


def distributor_sets_chart():
    qs = get_data().values('distributor').order_by('distributor')\
        .annotate(count=Count('serial')).values_list('distributor', 'count')
    names, counts = zip(*qs)
    names = [str(n) for n in names]
    plt.barh(names, counts)

    plt.xlabel("Sets in possession")
    plt.ylabel("Distributors")
    plt.title("Sets by distributor")

    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data
