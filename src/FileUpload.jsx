import React, { useState } from 'react';
import { ChakraProvider, Button, Heading, Box, Input, FormControl, FormLabel, VStack, HStack } from "@chakra-ui/react";

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [file, setFile] = useState(null);
  const [meterData, setMeterData] = useState({ maxValue: '', minValue: '' }); // 追加

  return (
    <ChakraProvider>
      <Box m={5}>
        <Heading mb={4}>autoread</Heading>
        <VStack spacing={5} align="stretch">
          <FileUpload setUploadedFile={setUploadedFile} setFile={setFile} />
          <ContentDisplay uploadedFile={uploadedFile} file={file} meterData={meterData} setMeterData={setMeterData} />
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

function FileUpload({ setUploadedFile, setFile }) {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedFile(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <FormControl>
      <Input type="file" onChange={handleFileChange} />
    </FormControl>
  );
}

function ContentDisplay({ uploadedFile, file, meterData, setMeterData }) {
  const handleAutoRead = async () => {
    if (!file) {
      alert('ファイルを選択してください。');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://auto-read.onrender.com/upload', { // ここにRenderのURLを記述
        method: 'POST',
        body: formData
      });
    
      if (!response.ok) {
        throw new Error('サーバーエラー');
      }    

      const result = await response.json(); // JSON形式でデータを受け取る

      // result.Endとresult.Startが数字かどうかをチェックして状態に保存
      const isNumeric = (value) => !isNaN(value) && !isNaN(parseFloat(value));
      setMeterData({
        maxValue: isNumeric(result.End) ? result.End : '',
        minValue: isNumeric(result.Start) ? result.Start : ''
      });

      // アップロードが成功した場合の処理
      alert('ファイルアップロード成功');
    } catch (error) {
      console.error('アップロードエラー:', error);
      alert('ファイルアップロード失敗。');
    }
  };

  return (
    <HStack align="start" spacing={10}>
      <ImageDisplay uploadedFile={uploadedFile} />
      <MeterForm handleAutoRead={handleAutoRead} meterData={meterData} />
    </HStack>
  );
}

function ImageDisplay({ uploadedFile }) {
  if (!uploadedFile) {
    return null;
  }
  return (
    <img src={uploadedFile} alt="アップロードされた画像" style={{ width: '500px', height: '500px', objectFit: 'cover' }} />
  );
}

function MeterForm({ handleAutoRead, meterData }) {
  const [meterName, setMeterName] = useState('');
  const [maxValue, setMaxValue] = useState('');
  const [minValue, setMinValue] = useState('');
  const [unit, setUnit] = useState('');
  const [value, setValue] = useState('');

  const handleDownload = () => {
    const data = {
      meterName,
      maxValue,
      minValue,
      unit,
      value,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'meterData.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <Box p={5} shadow="md" borderWidth="1px">
      <FormControl mb={4}>
        <FormLabel>メーターの名前</FormLabel>
        <Input type="text" value={meterName} onChange={(e) => setMeterName(e.target.value)} />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>最大値</FormLabel>
        <Input type="text" value={maxValue || meterData.maxValue} onChange={(e) => setMaxValue(e.target.value)} />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>最小値</FormLabel>
        <Input type="text" value={minValue || meterData.minValue} onChange={(e) => setMinValue(e.target.value)} />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>単位</FormLabel>
        <Input type="text" value={unit} onChange={(e) => setUnit(e.target.value)} />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>値</FormLabel>
        <Input type="text" value={value} onChange={(e) => setValue(e.target.value)} />
      </FormControl>
      <Button colorScheme="blue" onClick={handleDownload}>
        JSONダウンロード
      </Button>
      <Button colorScheme="orange" onClick={handleAutoRead}>
        自動読み取り
      </Button>
    </Box>
  );
}

export default App;
