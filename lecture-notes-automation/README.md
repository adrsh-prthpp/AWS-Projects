# Lecture Notes Automation 
This project automates the conversion of recorded lecture audio files into summarized notes using AWS services. When an audio file is uploaded to S3, the system transcribes it and extracts key phrases and entities to generate concise notes, which are then saved back to S3.

---

## 🧩 Architecture Overview

- **Trigger**: S3 `PUT` event (lecture upload)
- **Compute**: AWS Lambda
- **Services Used**:
  - Amazon S3 (Storage and Event trigger)
  - Amazon Transcribe (Speech-to-text)
  - Amazon Comprehend (NLP: key phrases, entities)
  - AWS IAM (permissions)
- **Output**: Summarized notes saved to a `summarized-notes/` folder in the same bucket

---

## ⚙️ Setup Steps

1. **Create an S3 Bucket**
   - Enable event notifications for object creation.
   - Set up two folders: `uploads/` for raw audio, and `summarized-notes/` for output.

2. **Create the IAM Role for the Lambda Function**
 
    Assign IAM permissions following least-privilege access:
   - S3
     - `s3:GetObject`
     - `s3:PutObject`
   - Transcribe
     - `transcribe:StartTranscriptionJob`
     - `transcribe:GetTranscriptionJob`
   - Comprehend
     - `comprehend:DetectKeyPhrases`
     - `comprehend:DetectEntities`

3. **Create the Lambda Function**
   - Runtime: Python 3.12
   - Upload the `lambda_function.py` file from this folder.
   - Set the S3 trigger to respond to `s3:ObjectCreated:*` events in the `uploads/` prefix.

4. **Test It**
   - Upload an audio file (e.g., `.mp3`, `.wav`) to `uploads/`.
   - Lambda will:
     1. Transcribe the audio
     2. Use Comprehend to extract phrases/entities
     3. Save a text file in `summarized-notes/`
