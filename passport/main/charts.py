import matplotlib.pyplot as plt
from io import StringIO
from .models import Set, Order
from django.db.models import OuterRef, Subquery


def get_data():
    qs = Set.objects.all()
    qs = qs.select_related('article')
    latest_order = Order.objects.filter(sets=OuterRef('pk')).order_by('-date')[:1]
    qs = qs.prefetch_related('order_set').annotate(recipient=Subquery(latest_order.values('recipient__name')),
                                                   distributor=Subquery(latest_order.values('distributor__name')),
                                                   city=Subquery(latest_order.values('city__name')),
                                                   )
    return qs


def distributor_sets_chart():
    # TODO refactor this
    qs = get_data().values_list('distributor', 'serial')
    new_data = {}
    for e in qs:
        if e[0] not in new_data:
            new_data[e[0]] = 1
        else:
            new_data[e[0]] += 1
    new_data['None'] = new_data.pop(None)

    y = list(new_data.keys())
    x = list(new_data.values())
    plt.barh(y, x)

    plt.xlabel("Sets in possession")
    plt.ylabel("Distributors")
    plt.title("Sets by distributor")

    imgdata = StringIO()
    plt.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data
