import json
import boto3
from botocore.exceptions import ClientError

# Initialize a session using Amazon DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserTable')  # Ensure this matches your DynamoDB table name

# Sample book metadata for demonstration purposes
# In a real-world scenario, this data would likely be stored in a larger database
books = [
    {"id": "1", "title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Fiction"},
    {"id": "2", "title": "1984", "author": "George Orwell", "genre": "Dystopian"},
    {"id": "3", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Fiction"},
    {"id": "4", "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "Non-Fiction"},
    {"id": "5", "title": "Educated", "author": "Tara Westover", "genre": "Biography"},
]

def lambda_handler(event, context):
    # Example event structure
    # event = {
    #     "userId": "user123",
    #     "preferences": {
    #         "genres": ["Fiction", "Biography"],
    #         "authors": ["Harper Lee", "Tara Westover"]
    #     }
    # }

    user_id = event.get('userId')
    preferences = event.get('preferences', {})

    if not user_id or not preferences:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input. Please provide userId and preferences.'})
        }

    # Fetch user data from DynamoDB
    try:
        response = table.get_item(Key={'id': user_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to retrieve user data.'})
        }

    user_data = response.get('Item')
    if not user_data:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'User not found.'})
        }

    # Merge user preferences
    user_preferences = user_data.get('preferences', {})
    user_preferences.update(preferences)

    # Save updated preferences back to DynamoDB
    try:
        table.update_item(
            Key={'id': user_id},
            UpdateExpression="set preferences = :p",
            ExpressionAttributeValues={
                ':p': user_preferences
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to update user preferences.'})
        }

    # Generate book recommendations based on preferences
    recommended_books = get_book_recommendations(user_preferences)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Recommendations generated successfully.',
            'recommendedBooks': recommended_books
        })
}

def get_book_recommendations(preferences):
    genres = preferences.get('genres', [])
    authors = preferences.get('authors', [])

    # Filter books based on preferences
    recommended_books = []
    for book in books:
        if book['genre'] in genres or book['author'] in authors:
            recommended_books.append(book)

    return recommended_books
