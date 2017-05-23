from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext

from website.forms import UserForm, ProductForm, PaymentTypeForm
from website.models import Product
from website.models import ProductType
from website.models import Profile
from website.models import PaymentType
# standard Django view: query, template name, and a render method to render the data from the query into the s

def index(request):
    """
    Purpose: renders the index page with a list of 20 (mpax)  products
    Author: Harper Frankstone
    Args: request -- the full HTTP request object
    Returns: rendered view of the index page, with a list of products
    """
    all_products = Product.objects.all().order_by('-id')[:20]
    template_name = 'index.html'
    return render(request, template_name, {'products': all_products})


def register(request):
    """Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    """

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # Create a new user by invoking the `create_user` helper method
    # on Django's built-in User model
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        return login_user(request)

    elif request.method == 'GET':
        user_form = UserForm()
        template_name = 'register.html'
        return render(request, template_name, {'user_form': user_form})


def login_user(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''

    # Obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # Use the built-in authenticate method to verify
        username=request.POST['username']
        password=request.POST['password']
        authenticated_user = authenticate(username=username, password=password)

        # If authentication was successful, log the user in
        if authenticated_user is not None:
            login(request=request, user=authenticated_user)
            return HttpResponseRedirect('/')

        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")


    return render(request, 'login.html', {}, context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage. Is there a way to not hard code
    # in the URL in redirects?????
    return HttpResponseRedirect('/')

@login_required(login_url='/login')
def sell_product(request):
    """
    Purpose: to present the user with a form to upload information about a product to sell
    Author: Boilerplate code
    Args: request -- the full HTTP request object
    Returns: a form that lets a user upload a product to sell
    """
    if request.method == 'GET':
        product_form = ProductForm()
        template_name = 'create.html'
        return render(request, template_name, {'product_form': product_form})

    elif request.method == 'POST':
        form_data = request.POST
        pt = ProductType.objects.get(pk=form_data['product_type'])
        p = Product(
            seller = request.user,
            title = form_data['title'],
            description = form_data['description'],
            price = form_data['price'],
            quantity = form_data['quantity'],
            product_type = pt,
        )
        p.save()
        template_name = 'success.html'
        return render(request, template_name, {})


def list_products(request):
    """
    Purpose: to render a view with a list of all products
    Author: Boilerplate code
    Args: request -- the full HTTP request object
    Returns: a rendered view of a list of products
    """
    all_products = Product.objects.all()
    template_name = 'list.html'
    return render(request, template_name, {'products': all_products})

def single_product(request, product_id):
    """
    purpose: Allows user to view product_detail view, which contains a very specific view
        for a singular product
        For an example, visit /product_details/1/ to see a view on the first product created
        displaying title, description, quantity, price/unit, and "Add to order" button

    author: Max Baldridge

    args: product_id: (integer): id of product we are viewing 

    returns: (render): a view of the request, template to use, and product obj
    """        
    template_name = 'single.html'
    product = get_object_or_404(Product, pk=product_id)            
    return render(request, template_name, {
        "product": product})

def list_product_types(request):
    """
    Purpose: To retrieve a list of all products & product_types from
    their respective tables so that a template may sort through and filter
    the results.
    Author: Jordan Nelson
    Args: None
    Returns: Combines a given template with a given context dictionary and 
    returns an HttpResponse object with that rendered text.
    """
    product_types = ProductType.objects.all().order_by('-pk')

    for pt in product_types:
        pt.num_products = pt.product_set.filter(product_type=pt.id).count()
        pt.products = pt.product_set.filter(product_type=pt.id).order_by('-pk')[:3]

    return render(request, 'product_types.html', {'product_types': product_types})




@login_required(login_url='/login')
def profile(request): 
    """
    Purpose: to render the profile page in the browser
    Author: Harper Frankstone
    Args: request -- the full HTTP request object
    Returns: 
    """
    template_name = 'profile.html'
    return render(request, template_name, {})


@login_required(login_url='/login')
def add_payment_type(request):
    """
    Purpose: to present the user with a form to add a payment type to their account
    Author: Aaron Barfoot
    Args: request -- the full HTTP request object
    Returns: a form that lets a user add a payment type to their account
    """
    if request.method == 'GET':
        payment_type_form = PaymentTypeForm()
        template_name = 'add_payment_type.html'
        return render(request, template_name, {'payment_type_form': payment_type_form})

    elif request.method == 'POST':
        form_data = request.POST
        pmt = PaymentType(
            customer = request.user,
            payment_type_name = form_data['payment_type_name'],
            account_number = form_data['account_number'],
        )
        pmt.save()
        template_name = 'payment_type_success.html'
        return render(request, template_name, {})

@login_required(login_url='/login')
def user_payment_types(request):
    """
    Purpose: To retrieve a list of all payment types associated with user
    Author: Aaron Barfoot
    Args: request -- the full HTTP request object
    Returns: list of payment types associated with current user.
    """
    user_payment_types = PaymentType.objects.filter(customer = request.user)
    template_name = 'user_payment_types.html'
    return render(request, 'user_payment_types.html', {'user_payment_types': user_payment_types})


# @login_required(login_url='/login')
# def add_product_to_cart(request, pk):
#         """
#     purpose: Allows user to add a product to their cart

#     author: Dara Thomas

#     args:  

#     returns: 
#     """  
#     product = models.Product.objects.get(id = pk)




# @login_required(login_url='/login')
# def view_cart(request):
#     """
#     purpose: Allows user to view cart and all products they've added to cart

#     author: Dara Thomas

#     args:  request -- The full HTTP request object

#     returns: rendered view of the cart page, with a list of products that are currently in the user's cart
#     """        
#     template_name = 'cart.html' 
#     products_in_cart =  models.Order.objects.get(user = request.user.id)
#     return render(request, template_name, {"product": product})



# @login_required(login_url='/login')
# def complete_order_add_payment():
#     """
#     purpose: Allows user to add a payment type to their order and therefore complete and place the order

#     author: Dara Thomas

#     args:  

#     returns: a checkout page where the user sees their order total and can select a payment type for their order
#     """    
#     template_name = 'checkout.html'

