import os
from types import MemberDescriptorType
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
# Create your views here.
from .models import voiture_collection
from .models import client_collection
from .models import reservation
from .models import reservation_collection

from bson.objectid import ObjectId  # Import ObjectId for generating unique IDs
from django.http import HttpResponseRedirect, HttpResponse
from bson import ObjectId
      
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.shortcuts import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime
from django.http import JsonResponse
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from .models import voiture_collection, client_collection  


# admin


from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from .models import user_collection 
from .models import manager_collection 
from .models import admin_collection 
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from .models import user_collection 
from .models import manager_collection 

from django.contrib import messages
from .models import admin_collection 
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import logout
import bcrypt


# ADMIN



@csrf_exempt  

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Find user in the database
        user = user_collection.find_one({'email': email})
        if user:
            # Compare stored hashed password with the user input
            stored_password = user['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                # User authenticated, store user information in session
                request.session['email'] = email
                request.session['user_type'] = user['type']
                
                # Check user type
                if user['type'] == 'admin':
                    admin = admin_collection.find_one({'user_id': user['_id']})
                    if admin and admin['archived'] == True:
                        return HttpResponse('<script>alert("Désolé, vous avez été supprimé."); window.location.href="/login";</script>')
                    else:
                        return redirect('dashboard')
                elif user['type'] == 'manager':
                    manager = manager_collection.find_one({'user_id': user['_id']})
                    if manager and manager['archived'] == True:
                        return HttpResponse('<script>alert("Désolé, vous avez été supprimé."); window.location.href="/login";</script>')
                    return redirect('index')
            else:
                # Incorrect password
                messages.error(request, "Correct your password")
        else:
            # User not found
            messages.error(request, "User doesn't exist")
            
    return render(request, 'login.html')


def dashboard(request):
    user_id = request.session.get('user_id')

    # Find all non-archived managers
    managers = list(manager_collection.find({"archived": False}))  
    # Find all non-archived admins
    admins = list(admin_collection.find({"archived": False}))  
    
    total_managers = manager_collection.count_documents({"archived": False})
    total_admins = admin_collection.count_documents({"archived": False})
    total_archived_managers = manager_collection.count_documents({"archived": True})

    # Fetch user details for each manager
    for manager in managers:
        user = user_collection.find_one({"_id": manager["user_id"]})
        if user:
            manager["email"] = user.get("email")
            manager["password"] = user.get("password")  # Only if you need the password, usually you should not expose it.

    # Fetch user details for each admin
    for admin in admins:
        user = user_collection.find_one({"_id": admin["user_id"]})
        if user:
            admin["email"] = user.get("email")
            admin["password"] = user.get("password")  # Only if you need the password, usually you should not expose it.

    context = {
        'manager': managers,
        'admin': admins,
        'user_id': user_id,
        'total_managers': total_managers,
        'total_admins': total_admins,
        'total_archived_managers': total_archived_managers,
    }
    
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render(context, request))


    
def modify(request, username):
    manager = manager_collection.find_one({'username': username})
    if manager:
            user = user_collection.find_one({"_id": manager["user_id"]})
            if user:
                manager["email"] = user.get("email")
                manager["password"] = user.get("password")  
    context = {
            'manager': manager
        }

    if request.method == 'POST':
        new_username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        tel = request.POST.get('tel')

        manager_collection.update_one(
            {'username': username},
            {'$set': {'username': new_username, 'name': name, 'tel': tel}}
        )
        user_collection.update_one(
        {'_id': manager['user_id']},
        {'$set': {'email': email}}
        )       
        return redirect('dashboard')
    template = loader.get_template('modify.html')
    return HttpResponse(template.render(context, request))
  

def modifyAdmin(request, username):
    admin = admin_collection.find_one({'username': username})
    if admin:
        user = user_collection.find_one({"_id": admin["user_id"]})
        if user:
            admin["email"] = user.get("email")
            admin["password"] = user.get("password")  
    context = {
        'admin': admin
    }
    if request.method == 'POST':
        new_username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        tel = request.POST.get('tel')
    
        
  
        
        admin_collection.update_one(
            {'username': username},
            {'$set': {'username': new_username, 'name': name, 'tel': tel}}
        )
        user_collection.update_one(
            {'_id': admin['user_id']},
            {'$set': {'email': email}}
        )

        # Redirect to a success page or do something else
        return redirect('dashboard')
        
    template = loader.get_template('modifyAdmin.html')
    return HttpResponse(template.render(context, request))
      
@csrf_exempt  

def ajouter(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        tel = request.POST.get('tel')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        user_type = request.POST.get('type')
        
        if password != confirm_password:
            return HttpResponse('<script>alert("Passwords do not match"); window.location.href="/add";</script>')
        
        # Encrypt the password
        encrypted_password = encrypt_password(password)
        
        if user_type == 'admin':
            admin_exists = admin_collection.find_one({'username': new_username})
            if admin_exists:
               return HttpResponse('<script>alert("Username already exists. Please choose another username."); window.location.href="/add";</script>')
            user_id = user_collection.insert_one({'email': email, 'password': encrypted_password, 'type': 'admin'}).inserted_id
            admin_collection.insert_one({'username': new_username, 'name': name, 'tel': tel, 'archived': False, 'user_id': user_id})
        elif user_type == 'manager':
            manager_exists = manager_collection.find_one({'username': new_username})
            if manager_exists:
                return HttpResponse('<script>alert("Username already exists. Please choose another username."); window.location.href="/add";</script>')
            user_id = user_collection.insert_one({'email': email, 'password': encrypted_password, 'type': 'manager'}).inserted_id
            manager_collection.insert_one({'username': new_username, 'name': name, 'tel': tel, 'archived': False, 'user_id': user_id})
        return redirect('dashboard')
    
    template = loader.get_template('add.html')
    return HttpResponse(template.render())

def encrypt_password(password):

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def supprimer(request, username):
    user_to_archive = manager_collection.find_one({'username': username})
    admin_to_archive = admin_collection.find_one({'username': username})
    if user_to_archive:
        manager_collection.update_one({'username': username}, {'$set': {'archived': True}})
        all_deleted_users = list(manager_collection.find({"archived": True}))
        for user in all_deleted_users:
            user_data = user_collection.find_one({"_id": user["user_id"]})
            if user_data:
                user["email"] = user_data.get("email")
                user["password"] = user_data.get("password")
        context = {'deleted_users': all_deleted_users}
        return render(request, 'delete.html', context)
    if admin_to_archive:
        admin_collection.update_one({'username': username}, {'$set': {'archived': True}})
        all_deleted_Admin = list(admin_collection.find({"archived": True}))
        for user in all_deleted_Admin:
            user_data = user_collection.find_one({"_id": user["user_id"]})
            if user_data:
                user["email"] = user_data.get("email")
                user["password"] = user_data.get("password")
        context = {'deleted_admin': all_deleted_Admin}
        return render(request, 'delete.html', context)
    else:
        # Handle case where user does not exist
        return HttpResponse("user_not_found.html")


def restore_user(request, username):
    archived_user = manager_collection.find_one({'username': username, 'archived': True})
    archived_admin = admin_collection.find_one({'username': username, 'archived': True})

    if archived_user:
        manager_collection.update_one({'username': username}, {'$set': {'archived': False}})
        return redirect('dashboard')
    if archived_admin:
        admin_collection.update_one({'username': username}, {'$set': {'archived': False}})
        return redirect('dashboard')
    else:
        # Handle case where archived user does not exist
        return HttpResponse("deleted user not found.")


def deleted_users_list(request):
    all_deleted_users = list(manager_collection.find({"archived": True}))
    for user in all_deleted_users:
        user_data = user_collection.find_one({"_id": user["user_id"]})
        if user_data:
            user["email"] = user_data.get("email")
            user["password"] = user_data.get("password")
  
    all_deleted_admin = list(admin_collection.find({"archived": True}))
    for admin in all_deleted_admin:
        admin_data = user_collection.find_one({"_id": admin["user_id"]})
        if admin_data:
            admin["email"] = admin_data.get("email")
            admin["password"] = admin_data.get("password")
    
    context = {'deleted_users': all_deleted_users,
               'deleted_admin': all_deleted_admin}
    return render(request, 'delete.html', context)

def logout_view(request):
        logout(request)
        return redirect('login')










# Manager



def index(request):
    # Retrieve data from MongoDB collections
    voitures = voiture_collection.find()
    voitures_list = list(voitures)
    
    clients = client_collection.find()
    clients_list = list(clients)
    
    reservations = reservation_collection.find()
    reservations_list = list(reservations)
    
    # Convert MongoDB object IDs to strings
    for voiture in voitures_list:
        voiture['id'] = str(voiture['_id'])
        
    for client in clients_list:
        client['id'] = str(client['_id'])
    
    # Calculate total number of cars and clients
    total_cars = len(voitures_list)
    total_clients = len(clients_list)
    total_reservations = len(reservations_list)
    
    # Calculate the count of accepted and refused reservations
    accepted_reservations = sum(1 for res in reservations_list if res['status'] == 'accepted')
    refused_reservations = sum(1 for res in reservations_list if res['status'] == 'refused')
    
    # Pass data to the template
    return render(request, 'manager/start.html', {'voitures': voitures_list, 'clients': clients_list, 'total_cars': total_cars, 'total_clients': total_clients, 'total_reservations': total_reservations, 'accepted_reservations': accepted_reservations, 'refused_reservations': refused_reservations})


# def getall(request):
#   voitures = voiture_collection.find()
#   voitures_list = list(voitures)  
#   return render(request, 'hello.html',{'voitures': voitures_list})

   


def ajouter_voiture_submit(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        marque = request.POST.get('marque')
        modele = request.POST.get('modele')
        annee = request.POST.get('annee')
        couleur = request.POST.get('couleur')
        kilometrage = request.POST.get('kilometrage')
        prix_location = request.POST.get('prix_location')
        capacity = request.POST.get('capacity')
        fuel_type = request.POST.get('fuel_type')
        transmission = request.POST.get('transmission')
        image = request.FILES.get('image')

        if image:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_name = image.name
        else:
            image_name = None

        new_id = str(ObjectId())

        record = {
            'matricule': matricule,
            'marque': marque,
            'modele': modele,
            'annee': annee,
            'couleur': couleur,
            'kilometrage': kilometrage,
            'prix_location': prix_location,
            'capacity': capacity,
            'fuel_type': fuel_type,
            'transmission': transmission,
            'image': image_name,
            'disponibilite': 1
        }

        # Insert the record into MongoDB collection
        voiture_collection.insert_one(record)
        
        # Redirect to index page after adding the car
        return redirect('voiture')

    else:
        return render(request, 'manager/ajouter_voiture.html')

def voiture(request):
  voitures = voiture_collection.find()
  voitures_list = list(voitures)
  
  clients = client_collection.find()
  client_list = list(clients)
  
  for voiture in voitures_list:
        voiture['id'] =  str(voiture['_id'])
        
  for client in client_list:
        client['id'] =  str(client['_id'])
  return render(request, 'manager/voiture.html' ,{'voitures': voitures_list, 'clients': client_list})

def supprimer_voiture(request, voiture_id):
    try:
        obj_id = ObjectId(voiture_id)  
        result = voiture_collection.delete_one({'_id': obj_id})
        voitures = voiture_collection.find()
        voitures_list = list(voitures) 
        if result.deleted_count == 1:
          return redirect('voiture')
        else:
            return HttpResponse("Voiture not found or could not be deleted")
    except Exception as e:
        return HttpResponse(f"Error occurred: {str(e)}")

def update_voiture_submit(request, voiture_id):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        marque = request.POST.get('marque')
        modele = request.POST.get('modele')
        annee = request.POST.get('annee')
        couleur = request.POST.get('couleur')
        capacity = request.POST.get('capacity')
        fuel_type = request.POST.get('fuel_type')
        transmission = request.POST.get('transmission')
        kilometrage = request.POST.get('kilometrage')
        prix_location = request.POST.get('prix_location')
        image = request.FILES.get('image')

        if image:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_name = image.name
        else:
            image_name = None

        obj_id = ObjectId(voiture_id)  

        # Retrieve the existing record from MongoDB using voiture_id
        existing_record = voiture_collection.find_one({'_id': obj_id})

        if existing_record:
            # Update the fields with new data
            updated_fields = {
                'matricule': matricule,
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'couleur': couleur,
                'capacity': capacity,
                'fuel_type': fuel_type,
                'transmission': transmission,
                'kilometrage': kilometrage,
                'prix_location': prix_location,
            }

            # If a new image is uploaded, update the image field
            if image_name:
                updated_fields['image'] = image_name

            # Save the updated record back to the database
            voiture_collection.update_one({'_id': obj_id}, {'$set': updated_fields})

        # Fetch all records again from MongoDB after update
        voitures = voiture_collection.find()
        voitures_list = list(voitures)
        
        # Redirect to the voiture page after update
        return redirect('voiture')

    else:
        return HttpResponse("Invalid request method.")

def change_dispo(request, voiture_id):
        obj_id = ObjectId(voiture_id)
        
        # Retrieve the current record from MongoDB using voiture_id
        existing_record = voiture_collection.find_one({'_id': obj_id})
        voitures = voiture_collection.find()
        voitures_list = list(voitures)
        for voiture in voitures_list:
          voiture['id'] =  str(voiture['_id'])
        if existing_record:
            current_status = existing_record.get('disponibilite', 0)
            
            # Check if the current availability status is 1
            if current_status == 1:
                # Toggle the availability status by updating it to 0
                voiture_collection.update_one({'_id': obj_id}, {'$set': {'disponibilite': 0}})
            else:
                # Toggle the availability status by updating it to 1
                voiture_collection.update_one({'_id': obj_id}, {'$set': {'disponibilite': 1}})
                
          
            # Render the voiture.html template after updating the availability status
            return redirect('voiture')
        
        else:
            # Handle the case where the record doesn't exist
            return HttpResponse("Error: Record not found")
    
    
    
    

# idont
def reserve_car(request, voiture_id):
        # Convert voiture_id to ObjectId
        obj_id = ObjectId(voiture_id)
        
        # Query the database for the car object
        voiture = voiture_collection.find_one({'_id': obj_id})
        
        # Check if voiture is found
        if voiture is None:
      
            return HttpResponse("voiture not found.", status=404)
          
        voiture['id'] =  str(voiture['_id'])
        
        # Pass the voiture object to the template rendering the reservation form
        return render(request, 'manager/reservation_form.html', {'voiture': voiture})

def submit_reservation(request, voiture_id):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        cin = request.POST.get('cin')  # Assuming you have a CIN field in your form
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        voiture_id = request.POST.get('voiture_id')

        # Convert voiture_id to ObjectId
        obj_id = ObjectId(voiture_id)

        # Check if CIN exists in the database
        cin_exists = client_collection.find_one({'cin': cin})
        if not cin_exists:
            return JsonResponse({'message': "CIN non trouvé dans la base de données. Veuillez vérifier votre CIN."}, status=400)

        car = voiture_collection.find_one({'_id': obj_id})
        if not car or car.get('disponibilite') != 1:
            return JsonResponse({'message': "Cette voiture n'est pas disponible pour la réservation."}, status=400)

        # Check if there's already a reservation for the same car and period
        existing_reservation = reservation.find_one({
            'voiture_id': voiture_id,
            'date_debut': {'$lte': date_fin},
            'date_fin': {'$gte': date_debut}
        })

        if existing_reservation:
            # Return a JSON response with the error message
            return JsonResponse({'message': "Cette voiture est déjà réservée pour cette période. Veuillez choisir d'autres dates."}, status=400)
        else:
            # Save the new reservation
            new_reservation = {
                'cin': cin,
                'date_debut': date_debut,
                'date_fin': date_fin,
                'voiture_id': voiture_id,
                'status': ""
            }
            reservation.insert_one(new_reservation)
            # Return a JSON response with the success message
            return JsonResponse({'message': "Réservation enregistrée avec succès!"})

    else:
        return HttpResponse("Méthode non autorisée.")







def ajouter_client_submit(request):
    if request.method == 'POST':
        # Extract all the form data
        nom = request.POST.get('nom_client')
        prenom = request.POST.get('prenom_client')
        cin = request.POST.get('cin_client')
        email = request.POST.get('email_client')
        telephone = request.POST.get('telephone_client')
        address = request.POST.get('address_client')
        image = request.FILES.get('image_client')

        if image:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_name = image.name
        else:
            image_name = None

        # Creating a new ID using ObjectId
        new_id = str(ObjectId())

        # Creating a record dictionary
        record = {
            'nom': nom,
            'prenom': prenom,
            'cin': cin,
            'email': email,
            'telephone': telephone,
            'address': address,
            'image': image_name
        }

        # Insert the record into MongoDB collection
        client_collection.insert_one(record)

        # Redirect to index page after adding the client
        return redirect('client')

    else:
        return render(request, 'manager/start.html')

def delete_client(request, client_id):
    try:
        obj_id = ObjectId(client_id)
        
        result = client_collection.delete_one({'_id': obj_id})
        
        if result.deleted_count == 1:
            return redirect('client')
        else:
            return HttpResponse("Client not found or could not be deleted")
    except Exception as e:
        return HttpResponse(f"Error occurred: {str(e)}")

def update_client_submit(request, client_id):
    if request.method == 'POST':
        image = request.FILES.get('image_client')
        nom = request.POST.get('nom_client')
        prenom = request.POST.get('prenom_client')
        cin = request.POST.get('cin_client')
        email = request.POST.get('email_client')
        telephone = request.POST.get('telephone_client')
        address = request.POST.get('address_client')

        if image:
            image_path = os.path.join(settings.MEDIA_ROOT, image.name)
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            image_name = image.name
        else:
            image_name = None

        obj_id = ObjectId(client_id)

        existing_record = client_collection.find_one({'_id': obj_id})

        if existing_record:
            existing_record['image'] = image_name if image_name else existing_record.get('image')
            existing_record['nom'] = nom
            existing_record['prenom'] = prenom
            existing_record['cin'] = cin
            existing_record['email'] = email
            existing_record['telephone'] = telephone
            existing_record['address'] = address

            client_collection.update_one({'_id': obj_id}, {'$set': existing_record})

    return redirect('client')

def client(request):
  voitures = voiture_collection.find()
  voitures_list = list(voitures)
  
  clients = client_collection.find()
  client_list = list(clients)
  
  for voiture in voitures_list:
        voiture['id'] =  str(voiture['_id'])
        
  for client in client_list:
        client['id'] =  str(client['_id'])
  return render(request, 'manager/clients.html' ,{'voitures': voitures_list, 'clients': client_list})






def show_reservation(request):
    reservations = reservation_collection.find()

    reservation_list = []
    for reservation in reservations:
        # Extracting reservation data
        reservation_data = {
            'id': str(reservation['_id']),
            'date_debut': reservation['date_debut'],
            'date_fin': reservation['date_fin'],
            'cin': reservation['cin'],
            'voiture_id': reservation['voiture_id'],
            'status' : reservation['status']
        }

        # Retrieving client data
        client = client_collection.find_one({'cin': reservation['cin']})
        if client:
            reservation_data['client'] = {
                'nom': client['nom'],
                'prenom': client['prenom'],
                'cin': client['cin'],
                'email': client['email'],
                'telephone': client['telephone'],
                'address': client['address'],
                'image': client['image']  # Assuming image is stored in client document
            }

        # Retrieving car data
        id= reservation['voiture_id']
        voiture = ObjectId(id)
        car = voiture_collection.find_one({'_id': voiture})
        if car:
            reservation_data['car'] = {
                'matricule': car['matricule'],
                'marque': car['marque'],
                'modele': car['modele'],
                'annee': car['annee'],
                'couleur': car['couleur'],
                'kilometrage': car['kilometrage'],
                'capacity': car['capacity'],
                'transmission': car['transmission'],
                'fuel_type': car['fuel_type'],
                'prix_location': car['prix_location'],
                'image': car['image']  # Assuming image is stored in car document
            }

        reservation_list.append(reservation_data)

    return render(request, 'manager/reservation.html', {'reservations': reservation_list})

def supprimer_reservation(request, reservation_id):
    try:
      
        obj_id = ObjectId(reservation_id)  # Convert reservation_id to ObjectId
        result = reservation_collection.delete_one({'_id': obj_id})  # Delete the reservation
        if result.deleted_count == 1:
            return redirect('reservation')  # Redirect to the index page after deletion
        else:
            return HttpResponse("Reservation not found or could not be deleted")
    except Exception as e:
        return HttpResponse(f"Error occurred: {str(e)}")
      
def accept_reservation(request, reservation_id):
    reservation_id_obj = ObjectId(reservation_id)
    reservation.update_one({'_id': reservation_id_obj}, {'$set': {'status': 'accepted'}})

    return redirect('reservation')  

def refuse_reservation(request, reservation_id):
    reservation_id_obj = ObjectId(reservation_id)

    reservation.update_one({'_id': reservation_id_obj}, {'$set': {'status': 'refused'}})

    return redirect('reservation')  

from datetime import datetime
from bson import ObjectId
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.http import HttpResponse

def generate_pdf(request, reservation_id):
    reservation = reservation_collection.find_one({'_id': ObjectId(reservation_id)})

    # Retrieve client information
    client = client_collection.find_one({'cin': reservation['cin']})

    # Retrieve car information
    car_id = ObjectId(reservation['voiture_id'])
    car = voiture_collection.find_one({'_id': car_id})

    # Calculate the number of days and the total price
    date_debut = datetime.strptime(reservation['date_debut'], '%Y-%m-%d')
    date_fin = datetime.strptime(reservation['date_fin'], '%Y-%m-%d')
    nb_jours = (date_fin - date_debut).days + 1  # Adding 1 to include the start date

    # Ensure prix_location is a number
    prix_location = car['prix_location']
    if isinstance(prix_location, str):
        try:
            prix_location = float(prix_location)
        except ValueError:
            prix_location = 0  # or handle the error as needed

    # Ensure nb_jours is a number
    if not isinstance(nb_jours, int):
        try:
            nb_jours = int(nb_jours)
        except ValueError:
            nb_jours = 0  # or handle the error as needed

    prix_total = prix_location * nb_jours

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Facture_{reservation_id}.pdf"'

    # Create a PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Define styles
    styles = getSampleStyleSheet()
    style_heading = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.white, backColor=colors.darkblue, spaceAfter=5, leftIndent=10, rightIndent=10, alignment=1)
    style_body = ParagraphStyle(name='BodyText', parent=styles['BodyText'], fontName='Helvetica', fontSize=12, textColor=colors.black, leftIndent=10, rightIndent=10, spaceAfter=10)
    style_bold = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold', textColor=colors.black, leftIndent=10, rightIndent=10, spaceAfter=10)

    # Add content to the PDF
    content = []

    # Add reservation information
    content.append(Paragraph("Information sur la Reservation ", style_heading))
    content.append(Paragraph(f"Reservation ID: <b>{reservation_id}</b>", style_body))
    content.append(Paragraph(f" Date Debut: <b>{reservation['date_debut']}</b>", style_body))
    content.append(Paragraph(f" Date Fin: <b>{reservation['date_fin']}</b>", style_body))
    content.append(Paragraph(f"Nombre de jours: <b>{nb_jours}</b>", style_body))
    content.append(Paragraph(f"Prix Total: <b>{prix_total} DH</b>", style_body))

   

    # Add client information
    if client:
        content.append(Spacer(1, 12))
        content.append(Paragraph("Information sur Client", style_heading))
        content.append(Paragraph(f"Name: <b>{client['nom']} {client['prenom']}</b>", style_body))
        content.append(Paragraph(f"Email: <b>{client['email']}</b>", style_body))
        content.append(Paragraph(f"Phone: <b>{client['telephone']}</b>", style_body))
        content.append(Paragraph(f"Address: <b>{client['address']}</b>", style_body))

    # Add car information
    if car:
        content.append(Spacer(1, 12))
        content.append(Paragraph("Information sur voiture", style_heading))
        content.append(Paragraph(f"Matricule: <b>{car['matricule']}</b>", style_body))
        content.append(Paragraph(f"Marque: <b>{car['marque']}</b>", style_body))
        content.append(Paragraph(f"Modèle : <b>{car['modele']}</b>", style_body))
        content.append(Paragraph(f"Année: <b>{car['annee']}</b>", style_body))
        content.append(Paragraph(f"Couleur : <b>{car['couleur']}</b>", style_body))
        content.append(Paragraph(f"Kilométrage : <b>{car['kilometrage']}</b>", style_body))
        content.append(Paragraph(f"Capacité : <b>{car['capacity']}</b>", style_body))
        content.append(Paragraph(f"Transmission: <b>{car['transmission']}</b>", style_body))
        content.append(Paragraph(f"Type de carburant: <b>{car['fuel_type']}</b>", style_body))
        content.append(Paragraph(f"Prix de location: <b>{car['prix_location']} DH/day</b>", style_body))

    # Add content to the document
    doc.build(content)

    return response
