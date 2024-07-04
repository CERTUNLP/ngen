import React from 'react'
import './FileUpload.css'
import { useTranslation, Trans } from 'react-i18next';

const FileUpload = ({ files, setFiles, removeFile }) => {
    const uploadHandler = (event) => {
        const filesToUpload = event.target.files;
        // se concatenan las 2 listas una lista con los archivos que fueron cargados (files)  y la otra lista con los que se agregaron recientemente
        setFiles([...files, ...filesToUpload]);
    }
    const { t } = useTranslation();

    return (
        <>
            <div className="file-card">
                <div className="file-inputs">
                    <input type="file" onChange={uploadHandler} multiple />
                    <button>
                        {t('file.upload')}
                    </button>
                </div>

                <p className="main">Se pueden subir archivos de tipo</p>
                <p className="info">PDF, JPG, PNG, TXT, DOC</p>

            </div>
        </>
    )
}

export default FileUpload
