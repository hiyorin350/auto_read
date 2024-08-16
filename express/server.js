const express = require('express');
const multer  = require('multer');
const app = express();
const port = 3000;

// ファイルの保存先とファイル名を設定
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/') // 保存先ディレクトリ
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname) // ファイル名
  }
})

const upload = multer({ storage: storage })

// CORS対策 (本番環境ではより安全な設定を推奨)
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header(
    'Access-Control-Allow-Headers',
    'Origin, X-Requested-With, Content-Type, Accept'
  );
  next();
});

// ファイルアップロードのエンドポイント
app.post('/upload', upload.single('file'), function (req, res, next) {
  // ファイルのアップロード成功
  res.status(200).json({ message: 'ファイルアップロード成功！' });//入っていない？
})

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
