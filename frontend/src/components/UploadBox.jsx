import { useState, useRef } from 'react'

const UploadBox = ({ onFileSelect }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState('')
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleFileInput = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleFile = (file) => {
    if (file.type === 'text/csv' || file.name.endsWith('.csv') || 
        file.type.includes('spreadsheet') || file.name.endsWith('.xlsx')) {
      setFileName(file.name)
      onFileSelect?.(file)
    } else {
      alert('Please upload a CSV or XLSX file')
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx"
        onChange={handleFileInput}
        style={{ display: 'none' }}
      />
      <div className="upload-icon">📁</div>
      <div className="upload-text">Drag & Drop CSV/XLSX File</div>
      <div className="upload-hint">or click to browse</div>
      {fileName && <div className="upload-file-name">{fileName}</div>}
    </div>
  )
}

export default UploadBox

