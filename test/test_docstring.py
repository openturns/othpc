import doctest
import othpc


def test_DistributedFunction_doctest():
    doctest.testmod(othpc.distributed_function, optionflags=doctest.ELLIPSIS)
