import doctest
import othpc


def test_submitfunction_doctest():
    doctest.testmod(othpc.submit_function, optionflags=doctest.ELLIPSIS)
