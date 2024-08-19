const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const app = express();
const port = process.env.PORT || 3000;

// MIMEタイプの設定
app.get('*.js', (req, res, next) => {
  res.type('application/javascript');
  next();
});

// JSX ファイルのルートに MIME タイプを設定
app.get('*.jsx', (req, res, next) => {
  res.type('application/javascript');
  next();
});

// Reactアプリケーションのビルドディレクトリを静的ファイルとして配信
app.use(express.static(path.join(__dirname, 'build')));
app.use(express.json()); // リクエストのボディをJSONとして解析
app.use(express.static('src'));

// ルートをReactアプリにリダイレクト
app.get('/*', (req, res) => {
  res.type('text/html');
  res.sendFile(path.join(__dirname, 'build', 'index.html'), (err) => {
    if (err) {
      res.status(500).send('Something went wrong!');
    }
  });
});

// ファイルの保存先とファイル名を設定
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/'); // 保存先ディレクトリ
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname); // ファイル名
  }
});
const upload = multer({ storage: storage });

// ファイルアップロードのエンドポイント
app.post('/upload', upload.single('file'), function (req, res, next) {
  const data = req.file; // クライアントから送られてきたデータ

  // Pythonスクリプトを実行し、データを渡す
  exec(`python3 /app/main.py '${data.path}'`, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      console.log(`stdout: ${stdout}`);
      console.error(`stderr: ${stderr}`);
      return res.status(500).send('Python script execution failed');
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
    }

    // printの出力結果を確認
    console.log(stdout);

    // ファイルのアップロード成功メッセージとPythonスクリプトの実行結果を一緒にクライアントに返却
    res.status(200).send(stdout);
  });
});


app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
