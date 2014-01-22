axpay
=====

Small project intended to overview payment for AX services.


Design
------

The association provides a number of base ``Service``.
The price of such services evolves with time, as noted in ``ServicePrice`` objects.

On the other side, a member registers a ``PaymentMode``; money is then taken from his
account through that payment mode, tracked in a ``CashFlow``.

This ``CashFlow`` may be used to pay for one or more services, maybe not for the current user,
as recoreded in a ``Payment``.
