/**
 * 文件上传 API
 */
import request from './request'

// 上传单张图片
export function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post('/upload/images', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 批量上传图片
export function uploadImages(files) {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  
  return request.post('/upload/images/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 上传视频
export function uploadVideo(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post('/upload/videos', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除文件
export function deleteFile(filePath) {
  return request.delete('/upload/files', {
    params: { file_path: filePath }
  })
}

export default {
  uploadImage,
  uploadImages,
  uploadVideo,
  deleteFile
}

