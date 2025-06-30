import json
import boto3
import urllib.parse
import urllib.request
import time

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
comprehend = boto3.client('comprehend')

def lambda_handler(event, context):
    try:
        # 1. Get file info from the S3 PUT event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        media_format = key.split('.')[-1]
        base_filename = key.split("/")[-1].rsplit('.', 1)[0]
        job_name = f"TranscriptionJob-{int(time.time())}"
        media_uri = f"s3://{bucket}/{key}"

        # 2. Start the transcription job
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': media_uri},
            MediaFormat=media_format,
            LanguageCode='en-US'
        )

        # 3. Wait for transcription to finish
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)

        if job_status == 'FAILED':
            raise Exception("Transcription job failed.")

        # 4. Get transcript text from URL
        transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        with urllib.request.urlopen(transcript_url) as response:
            transcript_data = json.loads(response.read())

        transcript_text = transcript_data['results']['transcripts'][0]['transcript']
        if not transcript_text.strip():
            raise ValueError("Transcript is empty.")

        # 5. Use Comprehend
        key_phrases = comprehend.detect_key_phrases(Text=transcript_text, LanguageCode='en')
        entities = comprehend.detect_entities(Text=transcript_text, LanguageCode='en')

        # 6. Create notes
        notes = "**Summary Notes**\n\n"
        notes += "**Key Phrases:**\n" + "\n".join(
            f"- {phrase['Text']}" for phrase in key_phrases['KeyPhrases'][:10]
        )
        notes += "\n\n**Entities:**\n" + "\n".join(
            f"- {entity['Type']}: {entity['Text']}" for entity in entities['Entities'][:10]
        )

        # 7. Save notes to summarized-notes/ folder in S3
        output_key = f"summarized-notes/{base_filename}-summarized.txt"
        s3.put_object(Bucket=bucket, Key=output_key, Body=notes.encode('utf-8'))

        return {
            'statusCode': 200,
            'body': f"Notes saved to {bucket}/{output_key}"
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }
