import logging

from google.cloud import storage
import pyarrow.csv as pv
import pyarrow.parquet as pq



def prepare_filename_hw3(dataset:str, **kwargs):
    filename_csv = f"{dataset}.csv"
    filename_parquet = filename_csv.replace('.csv', '.parquet')

    task_instance = kwargs['ti']
    task_instance.xcom_push(key="filename_csv", value=filename_csv)
    task_instance.xcom_push(key="filename_parquet", value=filename_parquet)
    logging.info("XCOM variables filename_csv and filename_parquet is successfully pushed..")

def prepare_filename(logical_date:str,dataset:str, **kwargs):
    
    file_identifier = "-".join(logical_date.split('-')[:-1])
    filename_csv = f"{dataset}_{file_identifier}.csv"
    filename_parquet = filename_csv.replace('.csv', '.parquet')

    task_instance = kwargs['ti']
    task_instance.xcom_push(key="filename_csv", value=filename_csv)
    task_instance.xcom_push(key="filename_parquet", value=filename_parquet)
    logging.info("XCOM variables filename_csv and filename_parquet is successfully pushed..")

def format_to_parquet(src_file:str):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    try:
        table = pv.read_csv(src_file)
        pq.write_table(table, src_file.replace('.csv', '.parquet'))
    except FileNotFoundError as e:
        logging.warning(f'FileNotFoundError: {src_file} does not exist')

def upload_to_gcs(bucket:str, object_name:str, local_file:str):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

