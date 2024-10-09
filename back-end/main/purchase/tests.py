from purchase.serializers import PurchaseSerializer, PurchaseMaterialSerializer, PurchaseToolSerializer
from purchase.models import Purchase, PurchaseReciept, PurchaseMaterial, PurchaseTool
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.hashers import make_password
from supplier.models import Supplier, SupplierAddress
from django.contrib.staticfiles.finders import find
from material.models import Material
from rest_framework import status
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from user.models import User
from tool.models import Tool

# Tests for purchase model
class TestPurchaseModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.material = Material.objects.create(name='material', size='2 inch X 4 inch X 8 feet', unit_cost=10.0, available_quantity=100)
        cls.tool = Tool.objects.create(name='tool', description='tool description', unit_cost=4.20, available_quantity=1)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.purchase_material = PurchaseMaterial.objects.create(purchase=cls.purchase, material=cls.material, quantity=10, cost=100.0)
        cls.purchase_tool = PurchaseTool.objects.create(purchase=cls.purchase, tool=cls.tool, quantity=26, cost=854.39)

    ## Test save method for purchase model
    def test_purchase_save(self):
        self.purchase.refresh_from_db()
        self.assertEqual(float(self.purchase.total), float(self.purchase.tax) + float(self.purchase_material.cost) + float(self.purchase_tool.cost))

    ## Test purchase save without pk (first time save)
    def test_purchase_save_without_pk(self):
        purchase = Purchase(supplier=self.supplier, supplier_address=self.address, tax=5.0, date=timezone.now().date())
        purchase.save()
        self.assertEqual(purchase.total, purchase.tax)

    ## Test save method for purchase material model
    def test_purchase_material_save(self):
        initial_quantity = self.material.available_quantity
        purchase_material = PurchaseMaterial.objects.create(purchase=self.purchase, material=self.material, quantity=10, cost=200.0)
        self.material.refresh_from_db()
        self.assertEqual(self.material.available_quantity, initial_quantity + purchase_material.quantity)
        self.assertEqual(self.material.unit_cost, purchase_material.cost / purchase_material.quantity)
        self.purchase.refresh_from_db()
        purchase_materials = PurchaseMaterial.objects.filter(purchase=self.purchase)
        purchase_tools = PurchaseTool.objects.filter(purchase=self.purchase)
        material_cost = sum(purchase_material.cost for purchase_material in purchase_materials)
        tool_cost = sum(purchase_tool.cost for purchase_tool in purchase_tools)
        expected_total = self.purchase.tax + material_cost + tool_cost
        self.assertAlmostEqual(self.purchase.total, expected_total, places=2)

    ## Test save method for purchase material model with zero quantity
    def test_purchase_material_save_zero_quantity(self):
        initial_quantity = self.material.available_quantity
        PurchaseMaterial.objects.create(purchase=self.purchase, material=self.material, quantity=0, cost=200.0)
        self.material.refresh_from_db()
        self.assertEqual(self.material.available_quantity, initial_quantity)
        self.assertEqual(self.material.unit_cost, 0.0)
        self.purchase.refresh_from_db()
        purchase_materials = PurchaseMaterial.objects.filter(purchase=self.purchase)
        purchase_tools = PurchaseTool.objects.filter(purchase=self.purchase)
        material_cost = sum(purchase_material.cost for purchase_material in purchase_materials)
        tool_cost = sum(purchase_tool.cost for purchase_tool in purchase_tools)
        expected_total = self.purchase.tax + material_cost + tool_cost
        self.assertAlmostEqual(self.purchase.total, expected_total, places=2)

    ## Test updating an existing purchase material
    def test_purchase_material_update(self):
        self.purchase_material.cost = 150.0
        self.purchase_material.save()
        self.purchase.refresh_from_db()
        self.assertAlmostEqual(float(self.purchase.total), float(self.purchase.tax) + 150.0 + float(self.purchase_tool.cost), places=2)

    ## Test delete method for purchase material
    def test_purchase_material_delete(self):
        initial_total = self.purchase.total
        self.purchase_material.delete()
        self.purchase.refresh_from_db()
        self.assertAlmostEqual(float(self.purchase.total), float(initial_total), places=2)

    ## Test save method for purchase tool model
    def test_purchase_tool_save(self):
        initial_quantity = self.tool.available_quantity
        purchase_tool = PurchaseTool.objects.create(purchase=self.purchase, tool=self.tool, quantity=10, cost=200.0)
        self.tool.refresh_from_db()
        self.assertEqual(self.tool.available_quantity, initial_quantity + purchase_tool.quantity)
        self.assertEqual(self.tool.unit_cost, purchase_tool.cost / purchase_tool.quantity)
        self.purchase.refresh_from_db()
        purchase_materials = PurchaseMaterial.objects.filter(purchase=self.purchase)
        purchase_tools = PurchaseTool.objects.filter(purchase=self.purchase)
        material_cost = sum(purchase_material.cost for purchase_material in purchase_materials)
        tool_cost = sum(purchase_tool.cost for purchase_tool in purchase_tools)
        expected_total = self.purchase.tax + material_cost + tool_cost
        self.assertAlmostEqual(self.purchase.total, expected_total, places=2)

    ## Test save method for purchase tool model with zero quantity
    def test_purchase_tool_save_zero_quantity(self):
        initial_quantity = self.tool.available_quantity
        PurchaseTool.objects.create(purchase=self.purchase, tool=self.tool, quantity=0, cost=200.0)
        self.tool.refresh_from_db()
        self.assertEqual(self.tool.available_quantity, initial_quantity)
        self.assertEqual(self.tool.unit_cost, 0.0)
        self.purchase.refresh_from_db()
        purchase_materials = PurchaseMaterial.objects.filter(purchase=self.purchase)
        purchase_tools = PurchaseTool.objects.filter(purchase=self.purchase)
        material_cost = sum(purchase_material.cost for purchase_material in purchase_materials)
        tool_cost = sum(purchase_tool.cost for purchase_tool in purchase_tools)
        expected_total = self.purchase.tax + material_cost + tool_cost
        self.assertAlmostEqual(self.purchase.total, expected_total, places=2)

    ## Test updating an existing purchase tool
    def test_purchase_tool_update(self):
        self.purchase_tool.cost = 150.0
        self.purchase_tool.save()
        self.purchase.refresh_from_db()
        self.assertAlmostEqual(float(self.purchase.total), float(self.purchase.tax) + 150.0 + float(self.purchase_material.cost), places=2)

    ## Test delete method for purchase tool
    def test_purchase_tool_delete(self):
        initial_total = self.purchase.total
        self.purchase_tool.delete()
        self.purchase.refresh_from_db()
        self.assertAlmostEqual(float(self.purchase.total), float(initial_total), places=2)

# Tests for purchase serializer
class TestPurchaseSerializer(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.reciept = SimpleUploadedFile(name='pergola-stain.jpg', content=open(find('pergola-stain.jpg'), 'rb').read(), content_type='image/jpg')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.empty_data = {'supplier': '', 'supplier_address': '', 'tax': '', 'total': '', 'date': '', 'uploaded_images': []}
        cls.negative_data = {'supplier': cls.supplier.pk, 'supplier_address': cls.address.pk, 'tax': -6.78, 'total': -6.78, 'date': timezone.now().date(), 'uploaded_images': [cls.reciept]}
        cls.valid_data = {'supplier': cls.supplier.pk, 'supplier_address': cls.address.pk, 'tax': 6.78, 'total': 6.78, 'date': timezone.now().date(), 'uploaded_images': [cls.reciept]}

    ## Test purchase serializer with empty data
    def test_purchase_serializer_empty_data(self):
        serializer = PurchaseSerializer(data=self.empty_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('supplier', serializer.errors)
        self.assertIn('supplier_address', serializer.errors)
        self.assertIn('date', serializer.errors)

    ## Test purchase serializer with negative data
    def test_purchase_serializer_negative_data(self):
        serializer = PurchaseSerializer(data=self.negative_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tax', serializer.errors)
        self.assertIn('total', serializer.errors)

    ## Test purchase serializer validation success
    def test_purchase_serializer_validation_success(self):
        serializer = PurchaseSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertIn('supplier', serializer.validated_data)
        self.assertIn('supplier_address', serializer.validated_data)
        self.assertIn('tax', serializer.validated_data)
        self.assertIn('total', serializer.validated_data)
        self.assertIn('date', serializer.validated_data)
        self.assertIn('uploaded_images', serializer.validated_data)

    def test_purchase_serializer_create(self):
        serializer = PurchaseSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        purchase = serializer.save()
        self.assertEqual(purchase.supplier, self.supplier)
        self.assertEqual(purchase.supplier_address, self.address)
        self.assertEqual(float(purchase.tax), 6.78)
        self.assertEqual(float(purchase.total), 6.78)
        self.assertEqual(purchase.images.count(), 1)

    def test_purchase_serializer_update(self):
        new_image = SimpleUploadedFile(name='pergola-stain.jpg', content=open(find('pergola-stain.jpg'), 'rb').read(), content_type='image/jpg')
        update_data = {
            'supplier': self.supplier.pk,
            'supplier_address': self.address.pk,
            'tax': 8.0,
            'total': 8.0,
            'date': timezone.now().date(),
            'uploaded_images': [new_image]
        }
        serializer = PurchaseSerializer(self.purchase, data=update_data)
        self.assertTrue(serializer.is_valid())
        purchase = serializer.save()
        self.assertEqual(purchase.tax, 8.0)
        self.assertEqual(purchase.total, 8.0)
        self.assertEqual(purchase.images.count(), 1)

class TestPuchaseMaterialSerializer(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.material = Material.objects.create(name='material', size='2 inch X 4 inch X 8 feet', unit_cost=10.0, available_quantity=100)
        cls.purchase_material = PurchaseMaterial.objects.create(purchase=cls.purchase, material=cls.material, quantity=10, cost=100.0)
        cls.empty_data = {'purchase': '', 'material': '', 'quantity': '', 'cost': ''}
        cls.negative_data = {'purchase': cls.purchase.pk, 'material': cls.material.pk, 'quantity': -10, 'cost': -73.29}
        cls.valid_data = {'purchase': cls.purchase.pk, 'material': cls.material.pk, 'quantity': 10, 'cost': 73.29}

    ## Test purchase material serializer with empty data
    def test_purchase_material_serializer_empty_data(self):
        serializer = PurchaseMaterialSerializer(data=self.empty_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('purchase', serializer.errors)
        self.assertIn('material', serializer.errors)
        self.assertIn('quantity', serializer.errors)
        self.assertIn('cost', serializer.errors)

    ## Test purchase material serializer with negative data
    def test_purchase_material_serializer_negative_data(self):
        serializer = PurchaseMaterialSerializer(data=self.negative_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)
        self.assertIn('cost', serializer.errors)

    ## Test purchase material serializer validation success
    def test_purchase_material_serializer_validation_success(self):
        serializer = PurchaseMaterialSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertIn('purchase', serializer.validated_data)
        self.assertIn('material', serializer.validated_data)
        self.assertIn('quantity', serializer.validated_data)
        self.assertIn('cost', serializer.validated_data)

class TestPuchaseToolSerializer(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.tool = Tool.objects.create(name='tool', unit_cost=10.0, available_quantity=100)
        cls.purchase_tool = PurchaseTool.objects.create(purchase=cls.purchase, tool=cls.tool, quantity=10, cost=100.0)
        cls.empty_data = {'purchase': '', 'tool': '', 'quantity': '', 'cost': ''}
        cls.negative_data = {'purchase': cls.purchase.pk, 'tool': cls.tool.pk, 'quantity': -10, 'cost': -73.29}
        cls.valid_data = {'purchase': cls.purchase.pk, 'tool': cls.tool.pk, 'quantity': 10, 'cost': 73.29}

    ## Test purchase tool serializer with empty data
    def test_purchase_tool_serializer_empty_data(self):
        serializer = PurchaseToolSerializer(data=self.empty_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('purchase', serializer.errors)
        self.assertIn('tool', serializer.errors)
        self.assertIn('quantity', serializer.errors)
        self.assertIn('cost', serializer.errors)

    ## Test purchase tool serializer with negative data
    def test_purchase_tool_serializer_negative_data(self):
        serializer = PurchaseToolSerializer(data=self.negative_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)
        self.assertIn('cost', serializer.errors)

    ## Test purchase tool serializer validation success
    def test_purchase_tool_serializer_validation_success(self):
        serializer = PurchaseToolSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertIn('purchase', serializer.validated_data)
        self.assertIn('tool', serializer.validated_data)
        self.assertIn('quantity', serializer.validated_data)
        self.assertIn('cost', serializer.validated_data)

class TestPurchaseView(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.password = 'test1234'
        cls.reciept_path = 'pergola-stain.jpg'
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().strftime('%Y-%m-%d'))
        cls.image = SimpleUploadedFile(name=cls.reciept_path, content=open(find(cls.reciept_path), 'rb').read(), content_type='image/jpg')
        cls.reciept = PurchaseReciept.objects.create(purchase=cls.purchase, image=cls.image)
        cls.empty_data = {'supplier': '', 'supplier_address': '', 'tax': '', 'total': '', 'date': ''}
        cls.negative_data = {'supplier': cls.supplier.pk, 'supplier_address': cls.address.pk, 'tax': -6.78, 'total': -6.78, 'date': timezone.now().strftime('%Y-%m-%d')}
        cls.create_data = {'supplier': cls.supplier.pk, 'supplier_address': cls.address.pk, 'tax': 6.78, 'total': 6.78, 'date': timezone.now().date(), 'uploaded_images': [SimpleUploadedFile(name=cls.reciept_path, content=open(find(cls.reciept_path), 'rb').read(), content_type='image/jpg')]}
        cls.update_data = {'supplier': cls.supplier.pk, 'supplier_address': cls.address.pk, 'tax': 10.29, 'total': 10.29, 'date': timezone.now().strftime('%Y-%m-%d')}
        cls.patch_data = {'date': timezone.now().date()}
        cls.list_url = reverse('purchase-list')
        cls.detail_url = lambda pk: reverse('purchase-detail', kwargs={'pk': pk})
        cls.reciept_url = lambda pk: reverse('purchase-picture-detail', kwargs={'pk': pk})
        cls.user = User.objects.create(first_name='first', last_name='last', email='firstlast@example.com', phone='1 (234) 567-8901', password=make_password(cls.password))

    ## Test get purchase not found
    def test_get_purchase_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(96))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Purchase Not Found.')

    ## Test get purchase success
    def test_get_purchase_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.purchase.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['supplier'], self.purchase.supplier.pk)
        self.assertEqual(response.data['supplier_address'], self.purchase.supplier_address.pk)
        self.assertEqual(float(response.data['tax']), self.purchase.tax)
        self.assertEqual(float(response.data['total']), self.purchase.total)
        self.assertEqual(response.data['date'], self.purchase.date)
        self.assertIn('images', response.data)

    ## Test get purchases success
    def test_get_purchases_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Purchase.objects.count())

    ## Test create purchase with empty data
    def test_create_purchase_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data=self.empty_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('supplier', response.data)
        self.assertIn('supplier_address', response.data)
        self.assertIn('date', response.data)

    ## Test create purchase with negative data
    def test_create_purchase_negative_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data=self.negative_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tax', response.data)
        self.assertIn('total', response.data)

    ## Test create purchase success
    def test_create_purchase_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Purchase.objects.count(), 2)
        purchase = Purchase.objects.filter(supplier=self.create_data['supplier'], supplier_address=self.create_data['supplier_address'], date=self.create_data['date'], tax=self.create_data['tax'], total=self.create_data['total'])
        self.assertTrue(purchase.exists())

    ## Test update purchase with empty data
    def test_update_purchase_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk), data=self.empty_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('supplier', response.data)
        self.assertIn('supplier_address', response.data)
        self.assertIn('date', response.data)

    ## Test update purchase with negative data
    def test_update_purchase_negative_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk), data=self.negative_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tax', response.data)
        self.assertIn('total', response.data)

    ## Test update purchase success
    def test_update_purchase_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk), data=self.patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        purchase = Purchase.objects.filter(date=self.patch_data['date'])
        self.assertTrue(purchase.exists())

    ## Test delete purchase reciept success
    def test_delete_purchase_reciept_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.reciept_url(self.reciept.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Purchase.objects.count(), 1)

    ## Test delete purchase success
    def test_delete_purchase_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.purchase.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Purchase.objects.count(), 0)

class TestPurchaseMaterialView(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.password = 'test1234'
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.material = Material.objects.create(name='material', size='2 inch X 4 inch X 8 feet', unit_cost=10.0, available_quantity=100)
        cls.purchase_material = PurchaseMaterial.objects.create(purchase=cls.purchase, material=cls.material, quantity=10, cost=100.0)
        cls.empty_data = {'purchase': '', 'material': '', 'quantity': '', 'cost': ''}
        cls.negative_data = {'purchase': cls.purchase.pk, 'material': cls.material.pk, 'quantity': -10, 'cost': -73.29}
        cls.create_data = {'purchase': cls.purchase.pk, 'material': cls.material.pk, 'quantity': 10, 'cost': 73.29}
        cls.update_data = {'purchase': cls.purchase.pk, 'material': cls.material.pk, 'quantity': 15, 'cost': 137.42}
        cls.patch_data = {'quantity': 16}
        cls.list_url = lambda purchase_pk: reverse('purchase-material-list', kwargs={'purchase_pk': purchase_pk})
        cls.detail_url = lambda purchase_pk, material_pk: reverse('purchase-material-detail', kwargs={'purchase_pk': purchase_pk, 'material_pk': material_pk})
        cls.user = User.objects.create(first_name='first', last_name='last', email='firstlast@example.com', phone='1 (234) 567-8901', password=make_password(cls.password))

    ## Test get purchase material not found
    def test_get_purchase_material_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.purchase.pk, 96))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Purchase Material Not Found.')

    ## Test get purchase material success
    def test_get_purchase_material_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.purchase.pk, self.purchase_material.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['material'], self.purchase_material.material.pk)
        self.assertEqual(response.data['quantity'], self.purchase_material.quantity)
        self.assertEqual(float(response.data['cost']), self.purchase_material.cost)

    ## Test get purchase materials success
    def test_get_purchase_materials_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url(self.purchase.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), PurchaseMaterial.objects.filter(purchase=self.purchase).count())

    ## Test create purchase material with empty data
    def test_create_purchase_material_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url(self.purchase.pk), data=self.empty_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('material', response.data)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test create purchase material with negative data
    def test_create_purchase_material_negative_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url(self.purchase.pk), data=self.negative_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test create purchase material success
    def test_create_purchase_material_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url(self.purchase.pk), data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseMaterial.objects.filter(purchase=self.purchase).count(), 2)
        purchase_material = PurchaseMaterial.objects.filter(purchase=self.create_data['purchase'], material=self.create_data['material'], quantity=self.create_data['quantity'], cost=self.create_data['cost'])
        self.assertTrue(purchase_material.exists())

    ## Test update purchase material with empty data
    def test_update_purchase_material_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk, self.purchase_material.pk), data=self.empty_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('material', response.data)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test update purchase material with negative data
    def test_update_purchase_material_negative_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk, self.purchase_material.pk), data=self.negative_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test update purchase material success
    def test_update_purchase_material_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk, self.purchase_material.pk), data=self.patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.purchase_material.refresh_from_db()
        self.assertEqual(self.purchase_material.quantity, self.patch_data['quantity'])

    ## Test delete purchase material success
    def test_delete_purchase_material_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.purchase.pk, self.purchase_material.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PurchaseMaterial.objects.filter(purchase=self.purchase_material.purchase, material=self.purchase_material.material, quantity=self.purchase_material.quantity, cost=self.purchase_material.cost).count(), 0)

class TestPurchaseNewMaterialView(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.password = 'test1234'
        cls.long_string = 't' * 501
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.material = Material.objects.create(name='material', size='2 inch X 4 inch X 8 feet', unit_cost=10.0, available_quantity=100, description='test')
        cls.purchase_material = PurchaseMaterial.objects.create(purchase=cls.purchase, material=cls.material, quantity=10, cost=100.0)
        cls.empty_material_data = {'name': '', 'description': '', 'size': '', 'quantity': 12, 'cost': 155.12}
        cls.short_material_data = {'name': 'f', 'description': 'test', 'size': 't', 'quantity': 12, 'cost': 115.58}
        cls.long_material_data = {'name': cls.long_string, 'description': cls.long_string, 'size': cls.long_string, 'quantity': 15, 'cost': 1613510351351565465153168138183138}
        cls.empty_purchase_data = {'name': 'first', 'description': 'test', 'size': 'test', 'quantity': '', 'cost': ''}
        cls.long_purchase_data = {'name': 'first', 'description': 'test', 'size': 'test', 'quantity': 15, 'cost': 135158151531818138138181811.15153135153}
        cls.negative_purchase_data = {'name': 'first', 'description': 'test', 'size': 'test', 'quantity': -49, 'cost': -694.39}
        cls.valid_data = {'name': 'second', 'description': 'test', 'size': 'size', 'quantity': 12, 'cost': 105.28}
        cls.existing_data = {'name': cls.material.name, 'description': cls.material.description, 'size': cls.material.size, 'quantity': 15, 'cost': 115.28}
        cls.url = lambda purchase_pk: reverse('purchase-new-material', kwargs={'purchase_pk': purchase_pk})
        cls.user = User.objects.create(first_name='first', last_name='last', email='firstlast@example.com', phone='1 (234) 567-8901', password=make_password(cls.password))

    def test_new_material_empty_material_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.empty_material_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('size', response.data)

    def test_new_material_short_material_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.short_material_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('size', response.data)

    def test_new_material_empty_purchase_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.empty_purchase_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    def test_new_material_long_purchase_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.long_purchase_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cost', response.data)

    def test_new_material_negative_purchase_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.negative_purchase_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    def test_new_material_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Material.objects.filter(name=self.valid_data['name'], description=self.valid_data['description'], size=self.valid_data['size']).exists())
        self.assertTrue(PurchaseMaterial.objects.filter(purchase=self.purchase, material__name=self.valid_data['name'], quantity=self.valid_data['quantity'], cost=self.valid_data['cost']).exists())

    def test_existing_material_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.existing_data)
        self.purchase_material.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PurchaseMaterial.objects.filter(purchase=self.purchase, material__name=self.existing_data['name'], quantity=self.existing_data['quantity'], cost=self.existing_data['cost']).exists())
        self.assertEqual(self.purchase_material.quantity, self.existing_data['quantity'])
        self.assertAlmostEqual(float(self.purchase_material.cost), self.existing_data['cost'], places=2)

class TestPurchaseToolView(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.password = 'test1234'
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.tool = Tool.objects.create(name='tool', unit_cost=10.0, available_quantity=100)
        cls.purchase_tool = PurchaseTool.objects.create(purchase=cls.purchase, tool=cls.tool, quantity=10, cost=100.0)
        cls.empty_data = {'purchase': '', 'tool': '', 'quantity': '', 'cost': ''}
        cls.negative_data = {'purchase': cls.purchase.pk, 'tool': cls.tool.pk, 'quantity': -10, 'cost': -73.29}
        cls.create_data = {'purchase': cls.purchase.pk, 'tool': cls.tool.pk, 'quantity': 10, 'cost': 73.29}
        cls.update_data = {'purchase': cls.purchase.pk, 'tool': cls.tool.pk, 'quantity': 15, 'cost': 137.42}
        cls.patch_data = {'quantity': 16}
        cls.list_url = lambda purchase_pk: reverse('purchase-tool-list', kwargs={'purchase_pk': purchase_pk})
        cls.detail_url = lambda purchase_pk, tool_pk: reverse('purchase-tool-detail', kwargs={'purchase_pk': purchase_pk, 'tool_pk': tool_pk})
        cls.user = User.objects.create(first_name='first', last_name='last', email='firstlast@example.com', phone='1 (234) 567-8901', password=make_password(cls.password))

    ## Test get purchase tool not found
    def test_get_purchase_tool_not_found(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.purchase.pk, 96))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Purchase Tool Not Found.')

    ## Test get purchase tool success
    def test_get_purchase_tool_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.purchase.pk, self.purchase_tool.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tool'], self.purchase_tool.tool.pk)
        self.assertEqual(response.data['quantity'], self.purchase_tool.quantity)
        self.assertEqual(float(response.data['cost']), self.purchase_tool.cost)

    ## Test get purchase tools success
    def test_get_purchase_tools_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url(self.purchase.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), PurchaseTool.objects.filter(purchase=self.purchase).count())

    ## Test create purchase tool with empty data
    def test_create_purchase_tool_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url(self.purchase.pk), data=self.empty_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tool', response.data)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test create purchase tool with negative data
    def test_create_purchase_tool_negative_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url(self.purchase.pk), data=self.negative_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test create purchase tool success
    def test_create_purchase_tool_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url(self.purchase.pk), data=self.create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseTool.objects.filter(purchase=self.purchase).count(), 2)
        purchase_tool = PurchaseTool.objects.filter(purchase=self.create_data['purchase'], tool=self.create_data['tool'], quantity=self.create_data['quantity'], cost=self.create_data['cost'])
        self.assertTrue(purchase_tool.exists())

    ## Test update purchase tool with empty data
    def test_update_purchase_tool_empty_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk, self.purchase_tool.pk), data=self.empty_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tool', response.data)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test update purchase tool with negative data
    def test_update_purchase_tool_negative_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk, self.purchase_tool.pk), data=self.negative_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    ## Test update purchase tool success
    def test_update_purchase_tool_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url(self.purchase.pk, self.purchase_tool.pk), data=self.patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.purchase_tool.refresh_from_db()
        self.assertEqual(self.purchase_tool.quantity, self.patch_data['quantity'])

    ## Test delete purchase tool success
    def test_delete_purchase_tool_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url(self.purchase.pk, self.purchase_tool.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PurchaseTool.objects.filter(purchase=self.purchase_tool.purchase, tool=self.purchase_tool.tool, quantity=self.purchase_tool.quantity, cost=self.purchase_tool.cost).count(), 0)

class TestPurchaseNewToolView(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.password = 'test1234'
        cls.long_string = 't' * 501
        cls.supplier = Supplier.objects.create(name='supplier')
        cls.address = SupplierAddress.objects.create(supplier=cls.supplier, street_address='123 Test Street', city='City', state='State', zip=12345)
        cls.purchase = Purchase.objects.create(supplier=cls.supplier, supplier_address=cls.address, tax=6.83, total=6.83, date=timezone.now().date())
        cls.tool = Tool.objects.create(name='tool', unit_cost=10.0, available_quantity=100, description='test')
        cls.purchase_tool = PurchaseTool.objects.create(purchase=cls.purchase, tool=cls.tool, quantity=10, cost=100.0)
        cls.empty_tool_data = {'name': '', 'description': '', 'quantity': 12, 'cost': 155.12}
        cls.short_tool_data = {'name': 'f', 'description': 'test', 'quantity': 12, 'cost': 115.58}
        cls.long_tool_data = {'name': cls.long_string, 'description': cls.long_string, 'quantity': 15, 'cost': 1613510351351565465153168138183138}
        cls.empty_purchase_data = {'name': 'first', 'description': 'test', 'quantity': '', 'cost': ''}
        cls.long_purchase_data = {'name': 'first', 'description': 'test', 'quantity': 15, 'cost': 135158151531818138138181811.15153135153}
        cls.negative_purchase_data = {'name': 'first', 'description': 'test', 'quantity': -49, 'cost': -694.39}
        cls.valid_data = {'name': 'second', 'description': 'test', 'quantity': 12, 'cost': 105.28}
        cls.existing_data = {'name': cls.tool.name, 'description': cls.tool.description, 'quantity': 15, 'cost': 115.28}
        cls.url = lambda purchase_pk: reverse('purchase-new-tool', kwargs={'purchase_pk': purchase_pk})
        cls.user = User.objects.create(first_name='first', last_name='last', email='firstlast@example.com', phone='1 (234) 567-8901', password=make_password(cls.password))

    def test_new_tool_empty_tool_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.empty_tool_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_new_tool_short_tool_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.short_tool_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_new_tool_empty_purchase_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.empty_purchase_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    def test_new_tool_long_purchase_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.long_purchase_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cost', response.data)

    def test_new_tool_negative_purchase_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.negative_purchase_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('cost', response.data)

    def test_new_tool_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tool.objects.filter(name=self.valid_data['name'], description=self.valid_data['description']).exists())
        self.assertTrue(PurchaseTool.objects.filter(purchase=self.purchase, tool__name=self.valid_data['name'], quantity=self.valid_data['quantity'], cost=self.valid_data['cost']).exists())

    def test_existing_tool_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(self.purchase.pk), data=self.existing_data)
        self.purchase_tool.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PurchaseTool.objects.filter(purchase=self.purchase, tool__name=self.existing_data['name'], quantity=self.existing_data['quantity'], cost=self.existing_data['cost']).exists())
        self.assertEqual(self.purchase_tool.quantity, self.existing_data['quantity'])
        self.assertAlmostEqual(float(self.purchase_tool.cost), self.existing_data['cost'], places=2)
