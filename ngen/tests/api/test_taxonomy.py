
from ngen.models import Taxonomy, NgenModel, NgenTreeModel, User  
from datetime import datetime, timedelta
from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status
from django.contrib.auth.hashers import make_password
from ngen.tests.api.test_authentication import BaseAPITestCase

from rest_framework_simplejwt.tokens import (
    AccessToken,
    RefreshToken,
    SlidingToken,
    Token,
    UntypedToken,
)

class MyToken(Token):
    token_type = "test"
    lifetime = timedelta(days=1)


class TaxonomyAPITestCase(APITestCase):

    fixtures = ["priority.json", "feed.json", "tlp.json", "user.json", "taxonomy.json", "state.json", "edge.json", "report.json", "network_entity.json", "network.json", "contact.json"]

    def setUp(self):
        basename = 'taxonomy'
        self.url = reverse(f'{basename}-list')
        url_login_jwt = reverse("token-create")
        json_login = {"username": "ngen", "password": "ngen"}
        resp = self.client.post(url_login_jwt, data=json_login, format="json")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp.data["access"])


    def test_list_taxonomy(self):
        """
        Test that taxonomies are being listed correctly
        """
        # Check if the taxonomies are being listed correctly
        response = self.client.get('/api/taxonomy/')         
        # Assertions for a successful response (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assertions to check the response content (e.g., JSON structure)
        # For example: self.assertEqual(len(response.data), 1)
    
    def test_create_taxonomy(self):
        """
        Test API taxonomy creation
        """
        # Simulating POST data
        taxonomy_data = {
            "type": "vulnerability",
            "name": "Test Taxonomy",
            "description": "",
        }
        
        # POST the data 
        response = self.client.post('/api/taxonomy/', taxonomy_data, format='json')  
        
        # Assertions for a successful creation (status code 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assertions to check the created object in the database (It is the last object in the database) // Forzar ID
        taxonomy = Taxonomy.objects.last()
        self.assertEqual(Taxonomy.objects.last(), taxonomy)
        self.assertEqual(taxonomy.name, 'Test Taxonomy')
    
    def test_update_taxonomy(self):
        """
        Test that taxonomies are being updated correctly
        """
        # Creating a test Taxonomy
        taxonomy = Taxonomy.objects.create(type='vulnerability', name='Old Name') 
        # Update data for the taxonomy
        updated_data = {
            "type": "vulnerability",
            "name": "Updated Name",
            "description": "",
        }
        # POST the data 
        response = self.client.put(f'/api/taxonomy/{taxonomy.id}/', updated_data, format='json')  
        
        # Assertions for a successful update (status code 200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assertions to check the object is updated in the database
        taxonomy.refresh_from_db()
        self.assertEqual(taxonomy.name, 'Updated Name')
    
    def test_delete_taxonomy(self):
        """
        Test that taxonomies are being deleted correctly
        """
        previous_length = taxonomy = Taxonomy.objects.count()
        # Creating a test taxonomy 
        taxonomy = Taxonomy.objects.create(type='vulnerability', name='Parent')
        response = self.client.delete(f'/api/taxonomy/{taxonomy.id}/')  

        # Assertions for a successful delete (status code 204)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertFalse(Taxonomy.objects.filter(id=Taxonomy.id).exists())


        """
        with self.assertRaises(Case.DoesNotExist):
            Case.objects.get(pk=case_pk)
        """