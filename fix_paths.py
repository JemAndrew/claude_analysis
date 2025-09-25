# save as fix_utils_import.py
from pathlib import Path

api_client = Path('src/core/api_client.py')
content = api_client.read_text(encoding='utf-8')

# Fix the import statement
content = content.replace(
    'from utils import batch_documents_for_api',
    'from core.utils import batch_documents_for_api'
)

# Also check for any other utils imports
content = content.replace(
    'from utils import',
    'from core.utils import'
)

api_client.write_text(content, encoding='utf-8')
print("✅ Fixed utils import in api_client.py")

# Also check if utils.py exists and has the function
utils_file = Path('src/core/utils.py')
if utils_file.exists():
    utils_content = utils_file.read_text(encoding='utf-8')
    if 'batch_documents_for_api' not in utils_content:
        print("⚠️  Warning: batch_documents_for_api not found in utils.py")
        print("   The API client may handle batching internally instead")