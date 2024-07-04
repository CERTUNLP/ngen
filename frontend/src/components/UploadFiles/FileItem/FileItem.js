import React from 'react'
import './FileItem.css'
import {Button} from 'react-bootstrap';

const FileItem = ({ index, file, deleteFile }) => {
    
    return (
        <>
            <li
                className="file-item"
                key={index}>
                <p>Nombre: {(file.original_filename||file.name)}</p>
                <p>Mime:   {file.mime}</p>
                <p>Tamaño: {file.size}</p>
                <p>Fecha de creacion: {file.created ? file.created.slice(0,10)+" "+file.created.slice(11,19): ""}</p>
                <div className="actions">
                    {!file.isUploading &&
                        <Button className='btn-icon btn-rounded' 
                            variant='outline-danger' 
                            onClick={() => deleteFile(index)}>
                           <i className='fas fa-trash-alt' />
                        </Button>
                    }
                </div>
            </li>
        </>
    )
}

export default FileItem
