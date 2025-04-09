import os
import json
import datetime
from django.conf import settings
from django.utils import timezone

# Notion API
try:
    from notion_client import Client as NotionClient
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False

# Microsoft Graph API (OneNote)
try:
    from msgraph.core import GraphClient
    MSGRAPH_AVAILABLE = True
except ImportError:
    MSGRAPH_AVAILABLE = False


class NotionService:
    """
    Dịch vụ tích hợp với Notion
    """

    def __init__(self, access_token):
        if not NOTION_AVAILABLE:
            raise ImportError("Thư viện notion_client không khả dụng. Vui lòng cài đặt thư viện này.")
        self.client = NotionClient(auth=access_token)

    def get_user_info(self):
        """Lấy thông tin người dùng"""
        try:
            response = self.client.users.me()
            return {
                'id': response['id'],
                'name': response.get('name', ''),
                'email': response.get('person', {}).get('email', '')
            }
        except Exception as e:
            raise Exception(f"Lỗi khi lấy thông tin người dùng Notion: {str(e)}")

    def get_databases(self):
        """Lấy danh sách databases"""
        try:
            response = self.client.search(filter={"property": "object", "value": "database"})
            return response.get('results', [])
        except Exception as e:
            raise Exception(f"Lỗi khi lấy danh sách databases từ Notion: {str(e)}")

    def create_page(self, database_id, title, content):
        """Tạo trang mới trong database"""
        try:
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }

            children = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ]

            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties,
                children=children
            )

            return {
                'id': response['id'],
                'url': response.get('url', '')
            }
        except Exception as e:
            raise Exception(f"Lỗi khi tạo trang mới trong Notion: {str(e)}")

    def get_page(self, page_id):
        """Lấy thông tin trang"""
        try:
            return self.client.pages.retrieve(page_id=page_id)
        except Exception as e:
            raise Exception(f"Lỗi khi lấy thông tin trang từ Notion: {str(e)}")

    def update_page(self, page_id, title=None, content=None):
        """Cập nhật trang"""
        try:
            # Cập nhật tiêu đề
            if title:
                self.client.pages.update(
                    page_id=page_id,
                    properties={
                        "Name": {
                            "title": [
                                {
                                    "text": {
                                        "content": title
                                    }
                                }
                            ]
                        }
                    }
                )

            # Cập nhật nội dung
            if content:
                # Lấy blocks hiện tại
                blocks = self.client.blocks.children.list(block_id=page_id)

                # Xóa blocks hiện tại
                for block in blocks.get('results', []):
                    self.client.blocks.delete(block_id=block['id'])

                # Thêm blocks mới
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": content
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                )

            return True
        except Exception as e:
            raise Exception(f"Lỗi khi cập nhật trang trong Notion: {str(e)}")


class OneNoteService:
    """
    Dịch vụ tích hợp với Microsoft OneNote (qua Microsoft Graph API)
    """

    def __init__(self, access_token):
        if not MSGRAPH_AVAILABLE:
            raise ImportError("Thư viện msgraph-core không khả dụng. Vui lòng cài đặt thư viện này.")
        self.client = GraphClient(access_token=access_token)

    def get_user_info(self):
        """Lấy thông tin người dùng"""
        try:
            response = self.client.get('/me')
            data = response.json()
            return {
                'id': data.get('id', ''),
                'name': data.get('displayName', ''),
                'email': data.get('mail', '') or data.get('userPrincipalName', '')
            }
        except Exception as e:
            raise Exception(f"Lỗi khi lấy thông tin người dùng OneNote: {str(e)}")

    def get_notebooks(self):
        """Lấy danh sách notebooks"""
        try:
            response = self.client.get('/me/onenote/notebooks')
            return response.json().get('value', [])
        except Exception as e:
            raise Exception(f"Lỗi khi lấy danh sách notebooks từ OneNote: {str(e)}")

    def get_sections(self, notebook_id):
        """Lấy danh sách sections trong notebook"""
        try:
            response = self.client.get(f'/me/onenote/notebooks/{notebook_id}/sections')
            return response.json().get('value', [])
        except Exception as e:
            raise Exception(f"Lỗi khi lấy danh sách sections từ OneNote: {str(e)}")

    def create_page(self, section_id, title, content):
        """Tạo trang mới trong section"""
        try:
            # Tạo nội dung HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
            </head>
            <body>
                <h1>{title}</h1>
                <p>{content}</p>
            </body>
            </html>
            """

            # Gửi yêu cầu tạo trang
            response = self.client.post(
                f'/me/onenote/sections/{section_id}/pages',
                headers={
                    'Content-Type': 'application/xhtml+xml'
                },
                data=html_content
            )

            data = response.json()
            return {
                'id': data.get('id', ''),
                'url': data.get('links', {}).get('oneNoteWebUrl', {}).get('href', '')
            }
        except Exception as e:
            raise Exception(f"Lỗi khi tạo trang mới trong OneNote: {str(e)}")

    def get_page_content(self, page_id):
        """Lấy nội dung trang"""
        try:
            response = self.client.get(f'/me/onenote/pages/{page_id}/content')
            return response.text
        except Exception as e:
            raise Exception(f"Lỗi khi lấy nội dung trang từ OneNote: {str(e)}")

    def update_page(self, page_id, content):
        """Cập nhật nội dung trang"""
        try:
            # OneNote API không hỗ trợ cập nhật toàn bộ trang
            # Thay vào đó, chúng ta cần cập nhật từng phần của trang

            # Cập nhật nội dung đoạn văn đầu tiên
            response = self.client.patch(
                f'/me/onenote/pages/{page_id}/content',
                headers={
                    'Content-Type': 'application/json'
                },
                json=[
                    {
                        'target': 'body',
                        'action': 'replace',
                        'content': f"<p>{content}</p>"
                    }
                ]
            )

            return response.status_code == 204  # No Content = success
        except Exception as e:
            raise Exception(f"Lỗi khi cập nhật trang trong OneNote: {str(e)}")


class NoteIntegrationService:
    """
    Dịch vụ tích hợp với các công cụ ghi chú
    """

    @staticmethod
    def get_service(provider, access_token):
        """Lấy dịch vụ tương ứng với provider"""
        if provider == 'notion':
            if not NOTION_AVAILABLE:
                raise ImportError("Thư viện notion_client không khả dụng. Vui lòng cài đặt thư viện này.")
            return NotionService(access_token)
        elif provider == 'onenote':
            if not MSGRAPH_AVAILABLE:
                raise ImportError("Thư viện msgraph-core không khả dụng. Vui lòng cài đặt thư viện này.")
            return OneNoteService(access_token)
        else:
            raise ValueError(f"Provider không được hỗ trợ: {provider}")

    @staticmethod
    def get_auth_url(provider):
        """Lấy URL xác thực cho provider"""
        if provider == 'notion':
            client_id = settings.NOTION_CLIENT_ID
            redirect_uri = settings.NOTION_REDIRECT_URI
            return f"https://api.notion.com/v1/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"
        elif provider == 'onenote':
            client_id = settings.MICROSOFT_CLIENT_ID
            redirect_uri = settings.MICROSOFT_REDIRECT_URI
            scopes = "Notes.Create Notes.Read Notes.ReadWrite User.Read"
            return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"
        else:
            raise ValueError(f"Provider không được hỗ trợ: {provider}")

    @staticmethod
    def exchange_code_for_token(provider, code):
        """Đổi code lấy token"""
        import requests

        if provider == 'notion':
            client_id = settings.NOTION_CLIENT_ID
            client_secret = settings.NOTION_CLIENT_SECRET
            redirect_uri = settings.NOTION_REDIRECT_URI

            response = requests.post(
                "https://api.notion.com/v1/oauth/token",
                headers={
                    "Content-Type": "application/json"
                },
                auth=(client_id, client_secret),
                json={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri
                }
            )

            if response.status_code != 200:
                raise Exception(f"Lỗi khi đổi code lấy token Notion: {response.text}")

            data = response.json()
            return {
                'access_token': data.get('access_token'),
                'refresh_token': None,  # Notion không cung cấp refresh token
                'expires_at': None,  # Notion không cung cấp thời gian hết hạn
                'account_info': {
                    'workspace_name': data.get('workspace_name'),
                    'workspace_id': data.get('workspace_id'),
                    'bot_id': data.get('bot_id')
                }
            }

        elif provider == 'onenote':
            client_id = settings.MICROSOFT_CLIENT_ID
            client_secret = settings.MICROSOFT_CLIENT_SECRET
            redirect_uri = settings.MICROSOFT_REDIRECT_URI

            response = requests.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )

            if response.status_code != 200:
                raise Exception(f"Lỗi khi đổi code lấy token OneNote: {response.text}")

            data = response.json()
            expires_in = data.get('expires_in', 3600)  # Mặc định 1 giờ
            expires_at = timezone.now() + datetime.timedelta(seconds=expires_in)

            # Lấy thông tin người dùng
            user_info = {}
            try:
                graph_client = GraphClient(access_token=data.get('access_token'))
                user_response = graph_client.get('/me')
                user_data = user_response.json()
                user_info = {
                    'id': user_data.get('id'),
                    'name': user_data.get('displayName'),
                    'email': user_data.get('mail') or user_data.get('userPrincipalName')
                }
            except Exception:
                pass

            return {
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'expires_at': expires_at,
                'account_info': user_info
            }

        else:
            raise ValueError(f"Provider không được hỗ trợ: {provider}")

    @staticmethod
    def refresh_token(provider, refresh_token):
        """Làm mới token"""
        import requests

        if provider == 'notion':
            # Notion không hỗ trợ refresh token
            return None

        elif provider == 'onenote':
            client_id = settings.MICROSOFT_CLIENT_ID
            client_secret = settings.MICROSOFT_CLIENT_SECRET

            response = requests.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )

            if response.status_code != 200:
                raise Exception(f"Lỗi khi làm mới token OneNote: {response.text}")

            data = response.json()
            expires_in = data.get('expires_in', 3600)  # Mặc định 1 giờ
            expires_at = timezone.now() + datetime.timedelta(seconds=expires_in)

            return {
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'expires_at': expires_at
            }

        else:
            raise ValueError(f"Provider không được hỗ trợ: {provider}")
