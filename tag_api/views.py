from collections import Counter
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django import forms
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from rest_framework.views import APIView
from django.db.models import Q
from django.utils.translation import gettext as _

from .models import TagsModel, VM, UserProfile
from .forms import tags_form, VMForm

import json

class Tags(APIView):
    """
    API view for handling CRUD operations on Tags.

    Methods:
    - get: Retrieve tags based on specified filters.
    - post: Create a new tag.
    - delete: Delete a tag if conditions are met.

    """

    def get(self, request):
        """
        Retrieve tags based on specified filters.

        This method handles GET requests to retrieve tags based on optional filters such as tag_id, tag_name, scope, and user_id.

        Parameters:
        - tag_id (optional): Filter tags by tag_id.
        - tag_name (optional): Filter tags by tag_name.
        - scope (optional): Filter tags by scope.
        - user_id (optional): Filter tags by user_id.

        """
        try:
            # Initialize filters for database queries
            filters = Q()

            # Check if tag_id is present in the request and add it to filters
            if request.method == 'GET' and 'tag_id' in request.GET:
                tag_id = request.GET['tag_id']
                filters &= Q(tag_id=tag_id)

            # Check if tag_name is present in the request and add it to filters
            if request.method == 'GET' and 'tag_name' in request.GET:
                tag_name = request.GET['tag_name']
                filters &= Q(tag_name__regex=tag_name)

            # Check if scope is present in the request and add it to filters
            if request.method == 'GET' and 'scope' in request.GET:
                scope = request.GET['scope']
                filters &= Q(scope__regex=scope)

            # Check if user_id is present in the request and add it to filters
            if request.method == 'GET' and 'user_id' in request.GET:
                user_id = request.GET['user_id']
                filters &= Q(user_id=user_id)

            # If no filters, get all tags data, else filter tags based on criteria
            if not filters:
                tags_data = TagsModel.objects.all().values()
            else:
                tags_data = TagsModel.objects.filter(filters).values()

            # Convert queryset to list for JsonResponse
            list_result = [entry for entry in tags_data]

            # Prepare and return JsonResponse
            data = {'status': 'success', 'error_code': 0, 'message': _("Tags get successfully"), 'data': list_result}
            return JsonResponse(data)

        except ValidationError as e:
            # Handle validation error
            data = {'status': 'error', 'error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except NameError as e:
            # Handle name error
            data = {'status': 'error', 'error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)


    def post(self, request):
        """
        Create a new tag.

        This method handles POST requests to create a new tag. It expects the following parameters
        in the POST data:
        - tag_name: Name of the tag
        - scope: Tag scope
        - user_id: User ID associated with the tag
        
        """
        try:

            # Parse the JSON data from the request
            json_data = json.loads(request.body.decode('utf-8'))
            
            # Validate the form data
            form = tags_form(request.POST)

            if form.is_valid():
                # Get tag_name, scope, and user_id from the POST data
                tag_name = request.data.get('tag_name')
                scope = request.data.get('scope') or None
                user_id = request.data.get("user_id")

                # Get user profile associated with the provided user_id
                user_profile = get_object_or_404(UserProfile, user_id=user_id)

                # Create a new TagsModel instance
                tag = TagsModel()
                tag.tag_name = tag_name
                tag.scope = scope
                tag.user_id = user_profile

                # Save the tag to the database
                # tag_data = tag.save()
                tag.save()

                # Prepare and return JsonResponse
                data = {'status': 'success', 'error_code': 0, 'message': _("Tag Added successfully"), 'data': ''}
                return JsonResponse(data)

        except ValidationError as e:
            # Handle validation error
            data = {'status': 'error', 'error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except NameError as e:
            # Handle name error
            data = {'status': 'error', 'error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except IntegrityError:
            # Handle the case of a duplicate tag name
            data = {'status': 'error', 'error_code': 102, 'message': _("This Tag Already exist")}
            return JsonResponse(data)


    def delete(self, request):
        """
        Delete a tag if conditions are met.

        This method handles DELETE requests to delete a tag. It expects the following parameters
        in the request:
        - tag_id: ID of the tag to be deleted
        - user_id: User ID making the request

        """
        try:
            # Get tag_id and user_id from the request parameters
            tag_id = request.GET.get('tag_id')
            user_id = request.GET.get('user_id')

            # Check if tag_id is provided
            if tag_id == None or tag_id == 'None' or tag_id == '':
                data = {'status': 'error', 'error_code': 100, 'message': _('Tag id is required')}
                return JsonResponse(data)

            # Check if user_id is provided
            if user_id == None or user_id == 'None' or user_id == '':
                data = {'status': 'error', 'error_code': 400, 'message': _("User id is required")}
                return JsonResponse(data)

            # Check if the tag is assigned to any VMs
            is_assigned = TagsModel.objects.filter(tag_id=tag_id, vms__isnull=False).exists()

            if is_assigned:
                data = {'status': 'error', 'error_code': 101,
                        'message': _("Tag is assigned to VMs. Unassign it before deleting.")}
                return JsonResponse(data)

            # Check if the user is admin or if the tag was created by the user
            is_admin = user_id == '1'
            is_exist = TagsModel.objects.filter(tag_id=tag_id, user_id__user_id=user_id).count()

            if is_admin or is_exist > 0:
                delete_tag = TagsModel.objects.filter(tag_id=tag_id).delete()
                data = {'status': 'success', 'error_code': 0, 'message': _("Tag deleted successfully.")}
                return JsonResponse(data)
            else:
                data = {'status': 'error', 'error_code': 100, 'message': _("Invalid Request.")}
                return JsonResponse(data)

        except NameError as e:
            # Handle NameError
            data = {'status': 'error', 'error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except KeyError as e:
            # Handle KeyError
            data = {'status': 'error', 'error_code': 102, 'message': "error: {0} is required".format(e)}
            return JsonResponse(data)

        except Exception as e:
            # Handle other exceptions
            data = {'status': 'error', 'error_code': 101, 'message': "error: {0}".format(e)}
            return JsonResponse(data)


# =====================================================================================================  
        
class AssignUnassignTags(APIView):
    def post(self, request):
        """
        Assign or unassign tags to/from objects.

        This method handles POST requests to assign or unassign tags to/from objects.
        It expects the following parameters in the request data:
        - action: 'assign' or 'unassign'
        - tag_name: Name of the tag
        - vm_ids: List of VM IDs to which the tag should be assigned or unassigned

        """
        try:
            # Get the action from the request data
            action = request.data.get("action")

            if action == 'assign':
                # Assign tags to objects
                tag_name = request.data.get('tag_name')
                vm_ids = request.data.get('vm_ids', [])

                # Get the tag instance
                tag = get_object_or_404(TagsModel, tag_name=tag_name)

                # Add the tag to the specified VMs
                tag.vms.add(*vm_ids)

                data = {'status': 'success', 'error_code': 0, 'message': _("Tag Assigned to Objects successfully"), 'data': ''}
                return JsonResponse(data)

            elif action == 'unassign':
                # Unassign tags from objects
                tag_name = request.data.get('tag_name')
                vm_ids = request.data.get('vm_ids', [])

                # Get the tag instance
                tag = get_object_or_404(TagsModel, tag_name=tag_name)

                # Remove the tag from the specified VMs
                tag.vms.remove(*vm_ids)

                data = {'status': 'success', 'error_code': 0, 'message': _("Tag Unassigned from Objects successfully"), 'data': ''}
                return JsonResponse(data)

            else:
                # Invalid action
                data = {'status': 'error', 'error_code': 108, 'message': _("Invalid action")}
                return JsonResponse(data)

        except ValidationError as e:
            # Handle ValidationError
            data = {'status': 'error', 'error_code': 103, 'message': "error: {0} ".format(e)}
            return JsonResponse(data)

        except Exception as e:
            # Handle other exceptions
            data = {'status': 'error', 'error_code': 101, 'message': "error: {0}".format(e)}
            return JsonResponse(data)


# =====================================================================================================  
        

class VMs(APIView):
    def get(self, request):
        """
        Retrieve VMs based on specified filters.

        This method handles GET requests to retrieve a list of Virtual Machines (VMs) based on optional filters. 
        Filters can include tag_name and scope to narrow down the selection.

        Parameters:
        - tag_name (optional): Filter VMs by the specified tag name.
        - scope (optional): Filter VMs by the specified tag scope.

        """
        try:
            vm_id = request.GET.get('vm_id')
            tag_names = request.GET.getlist('tag_name')
            scopes = request.GET.getlist('scopes')
            # print(scopes)

            queryset = VM.objects.all()

            if vm_id:

                # Include details of the specific VM if vm_id is provided
                vm_instance = get_object_or_404(VM, vm_id=vm_id)
                vm_data = [{'vm_id':vm_id, 'vm_name': vm_instance.vm_name, 'tags': [{'tag_name': tag.tag_name, 'scope': tag.scope} for tag in vm_instance.tags.all()]}]

            else:
                # if tag_names:
                #     # Filter VMs by tag names (case-insensitive)
                #     for tag_name in tag_names:
                #         queryset = queryset.filter(tags__tag_name__iexact=tag_name)

                if tag_names:
                    # Construct an OR query for tag_names
                    or_query = Q()
                    for tag_name in tag_names:
                        or_query |= Q(tags__tag_name__iexact=tag_name.strip())
                    vm_ids = queryset.filter(or_query).values_list('vm_id', flat=True).distinct()
                    queryset = queryset.filter(vm_id__in=vm_ids)

                if scopes:
                    # Filter VMs by tag scopes (case-insensitive)
                    for scope in scopes:
                        queryset = queryset.filter(tags__scope__regex=scope.strip())


                # Include information about tags using Prefetch
                vm_instances = queryset.prefetch_related('tags').all()

                vm_data = [{'vm_id':vm_id, 'vm_name': vm_instance.vm_name, 'tags': [{'tag_name': tag.tag_name, 'scope': tag.scope} for tag in vm_instance.tags.all()]} for vm_instance in vm_instances]

            vm_list_result = [entry for entry in vm_data]

            data = {'status': 'success', 'error_code': 0, 'message': _("VMs retrieved successfully"), 'data': vm_list_result}
            return JsonResponse(data)
        
        except Exception as e:
            # Handle any unexpected errors
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)
        
        

    def post(self, request):
        """
        Create a new Virtual Machine (VM) instance.

        This method handles POST requests to create a new VM. It expects the following parameters
        in the request data:
        - vm_name: Name of the VM.
        - tags (optional): List of tag-scope pairs (e.g., tag1:scope1, tag2:scope2) or a single tag-scope pair.
        - user_id: User ID associated with the VM.

        The method checks for the existence of a VM with the same name and creates a new VM instance if it doesn't exist.
        It associates the VM with tags provided in the tags parameter or creates new tags.

        """
        try:
            # Validate the form data
            form = VMForm(request.POST)
            
            # Extract parameters from the request
            vm_name = request.data.get("vm_name")
            tags = request.data.get("tags")
            user_id = request.data.get("user_id")

            # Check if VM instance with the same name already exists
            existing_vm = VM.objects.filter(vm_name=vm_name).exists()

            if existing_vm:
                data = {'status': 'error', 'error_code': 102, 'message': _("This VM Already exists.")}
                return JsonResponse(data)

            # Get or create the VM instance
            vm_instance = VM.objects.create(vm_name=vm_name)
            
            # Associate tags with the VM instance
            if tags:
                user_profile = get_object_or_404(UserProfile, user_id=user_id)

                # If tags is a single string, convert it to a list for consistency
                # if ',' in tags:
                #     tag_scopes = tags.split(',')
                # else:
                    # tag_scopes = [tags]

                for tag_scope in tags:
                    tag_name, scope = tag_scope.split(':')
                    tag_instance = TagsModel.objects.filter(tag_name=tag_name, scope=scope).first()

                    if tag_instance is None:
                        tag_instance = TagsModel.objects.create(tag_name=tag_name, scope=scope, user_id=user_profile)

                    vm_instance.tags.add(tag_instance)

            data = {'status': 'success', 'error_code': 0, 'message': _("VM added successfully."), 'data': ''}
            return JsonResponse(data)
        
        except ValidationError as e:
            # Handle validation error
            vm_instance.delete()
            data = {'status': 'error', 'error_code': 103, 'message': f"Validation error: {e}"}
            return JsonResponse(data)
        
        
        except Exception as e:
            # Handle any unexpected errors
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)


    def put(self, request):
        """
        Update an existing Virtual Machine (VM) with new information.

        This method handles PUT requests to update an existing VM with new data. The request data should include
        the following parameters:
        - id: ID of the VM to be updated.
        - vm_name (optional): New name for the VM.
        - tags (optional): List of tag IDs to be associated with the VM.

        The method retrieves the existing VM instance based on the provided ID, validates the new data using a form,
        and then updates the VM with the new information. It specifically updates the VM's name and associated tags.
        If the provided tag IDs include existing tags, they will be associated with the VM.

        """
        try:
            vm_instance = VM.objects.get(id=request.data.get('id'))
            form = VMForm(request.data, instance=vm_instance)

            if form.is_valid():
                # Save VM without committing to the database
                updated_vm_instance = form.save(commit=False)

                # Get tag IDs from the request
                tag_ids = request.data.getlist('tags')

                # Assign tags to the updated VM instance
                updated_vm_instance.tags.set(tag_ids)

                # Save the updated VM instance to the database
                updated_vm_instance.save()

                data = {'status': 'success', 'error_code': 0, 'message': _("VM updated successfully"), 'data': ''}
                return JsonResponse(data)
            else:
                # Validation error in the form
                data = {'status': 'error', 'error_code': 103, 'message': f"Validation Error: {form.errors}"}
                return JsonResponse(data)

        except VM.DoesNotExist:
            # VM with the provided ID not found
            data = {'status': 'error', 'error_code': 100, 'message': _("VM not found")}
            return JsonResponse(data)

        except Exception as e:
            # Handle any unexpected errors
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)


    def delete(self, request, vm_id):
        """
        Delete a Virtual Machine (VM) based on the provided ID.

        This method handles DELETE requests to delete a VM with the specified ID.
        
        Parameters (in URL):
        - vm_id: ID of the VM to be deleted.

        """
        try:
            vm = VM.objects.get(id=vm_id)
            vm.delete()

            data = {'status': 'success', 'error_code': 0, 'message': _("VM deleted successfully")}
            return JsonResponse(data)

        except VM.DoesNotExist:
            # VM with the provided ID not found
            data = {'status': 'error', 'error_code': 100, 'message': _("VM not found")}
            return JsonResponse(data)

        except Exception as e:
            # Handle any unexpected errors
            data = {'status': 'error', 'error_code': 101, 'message': f"Error: {e}"}
            return JsonResponse(data)

# ==============================================================================

class Users(APIView):
    def get(self, request):
         # Retrieve all user profiles from the database
        user_data = UserProfile.objects.all()

        # Create a list of dictionaries containing user_id and user_name for each user
        users = [{'user_id': user.user_id, 'user_name': user.user_name} for user in user_data]

        # Return the user data as a JSON response
        return JsonResponse({'users': users})