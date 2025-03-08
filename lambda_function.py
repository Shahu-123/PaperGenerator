import boto3
import sqlite3
from PIL import Image
import tempfile
import io
import generator
import json
import base64
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_random_question(db_path, topic=None, subject_id=None):
    """
    Get a random question from the database
    """
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            
            # Debug logging for subject ID and topic
            logger.info(f"Received subject_id: {subject_id}, type: {type(subject_id)}")
            logger.info(f"Received topic: {topic}, type: {type(topic)}")
            
            # Determine which table to query based on subject ID
            table_name = "QuestionsAdd" if subject_id == "0606" else "Questions"
            logger.info(f"Selected table: {table_name} based on subject_id comparison")
            
            # First, check if the table exists
            table_check_sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            logger.info(f"Executing table check SQL: {table_check_sql}")
            cursor.execute(table_check_sql)
            if not cursor.fetchone():
                logger.error(f"{table_name} table not found in database")
                return None
            
            # List all tables in database for debugging
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"Available tables in database: {tables}")
            
            # Get table schema for debugging
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            logger.info(f"Schema for {table_name}: {schema}")
            
            # Build the WHERE clause based on parameters
            where_clause = []
            params = []
            
            if topic:
                # Get all available topics first
                topics_sql = f"SELECT DISTINCT Topic FROM {table_name}"
                logger.info(f"Executing topics query: {topics_sql}")
                cursor.execute(topics_sql)
                available_topics = [row[0] for row in cursor.fetchall()]
                logger.info(f"Available topics in {table_name}: {available_topics}")
                
                # Try to find a matching topic (case-insensitive)
                matching_topic = next(
                    (db_topic for db_topic in available_topics 
                     if db_topic and topic and db_topic.lower() == topic.lower()),
                    None
                )
                
                if matching_topic:
                    where_clause.append("Topic = ?")
                    params.append(matching_topic)
                    logger.info(f"Matched topic '{topic}' to database topic '{matching_topic}'")
                else:
                    logger.warning(f"No matching topic found for '{topic}' in {table_name}")
            
            where_sql = " AND ".join(where_clause) if where_clause else "1=1"
            
            # Get count of available questions
            count_sql = f"SELECT COUNT(*) FROM {table_name} WHERE {where_sql}"
            logger.info(f"Executing count SQL: {count_sql} with params: {params}")
            cursor.execute(count_sql, params)
            count = cursor.fetchone()[0]
            logger.info(f"Found {count} questions in {table_name} for topic: {topic if topic else 'all'}")
            
            if count == 0:
                logger.error(f"No questions found in {table_name} for topic: {topic if topic else 'all'}")
                return None
            
            # Get a random question based on filters
            question_sql = f"""
                SELECT Image, Topic, Marks, Year, Month, Variant, Paper
                FROM {table_name} 
                WHERE {where_sql}
                ORDER BY RANDOM() 
                LIMIT 1
            """
            logger.info(f"Executing question SQL: {question_sql} with params: {params}")
            cursor.execute(question_sql, params)
            
            result = cursor.fetchone()
            if result:
                # Convert BLOB to base64
                image_base64 = base64.b64encode(result[0]).decode('utf-8') if result[0] else None
                logger.info(f"Successfully retrieved question from {table_name} for topic: {result[1]}")
                return {
                    'image': image_base64,
                    'topic': result[1],
                    'marks': result[2],
                    'year': result[3],
                    'month': result[4],
                    'variant': result[5],
                    'paper': result[6]
                }
            logger.error(f"No question found after query in {table_name}")
            return None
            
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

def lambda_handler(event, context):
    try:
        # Initialize S3 client
        s3 = boto3.client('s3')

        # Download the SQLite database file from S3
        s3_bucket = 'shahu-exam'
        s3_key = 'examcopy.db'
        local_file_path = '/tmp/my-database.db'
        s3.download_file(s3_bucket, s3_key, local_file_path)
        
        # Check if this is a random question request
        if event.get('action') == 'random_question':
            logger.info("Processing random question request")
            question_data = get_random_question(
                local_file_path, 
                event.get('topic'),
                event.get('subjectId')
            )
            if question_data:
                logger.info("Successfully generated random question")
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST,OPTIONS'
                    },
                    'body': json.dumps(question_data)
                }
            else:
                logger.error("Failed to generate random question")
                return {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'POST,OPTIONS'
                    },
                    'body': json.dumps({'error': 'No questions found'})
                }
        
        # Original paper generation logic
        logger.info("Processing paper generation request")
        raw_paper = generator.exam(event['topic'], event['mark'], event['subjectId'], event['info'])
        if raw_paper == "Error":
            url = "Error"
        else:
            x = raw_paper[0]
            pdf_filename = "/tmp/shahu.pdf"
            x.save(pdf_filename, "PDF", resolution=100.0, save_all=True, append_images=raw_paper[1:])
            object_name = "new-exam.pdf"
            s3.upload_file(pdf_filename, "shahu-exam", object_name)
            
            url = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': 'shahu-exam',
                    'Key': object_name
                },
                ExpiresIn=3600  # URL will expire in 1 hour
            )
            
            with open(pdf_filename, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
                base64_pdf_data = base64.b64encode(pdf_data).decode('utf-8')

        response = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'url': url})
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }
