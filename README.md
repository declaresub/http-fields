# http-headers



## Usage




    header = Header(name, value) # returns a Header object.  name and value are checked
    # for validity.


    header = Header.create(name, value) # returns a subclass of Header
    # if name corresponds to a header subclass, otherwise returns a Header object


    host = Host('example.com')

    def __init__(self, value=None, *, hostname:str =None)




## Unit tests

    pytest --cov=src --cov-report term-missing tests