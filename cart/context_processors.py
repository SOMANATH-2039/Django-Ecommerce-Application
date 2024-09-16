from .cart import Cart

#create context prosessor to our cart

def cart(request):


    return {'cart':Cart(request)}