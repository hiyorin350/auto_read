import React, { useState } from "react";
import {
  ChakraProvider,
  Button,
  Heading,
  Box,
  Input,
  FormControl,
  FormLabel,
  VStack,
  HStack,
  Progress,
} from "@chakra-ui/react";
import { motion } from "framer-motion";  // framer-motionのimport

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [file, setFile] = useState(null);
  const [meterData, setMeterData] = useState({ maxValue: "", minValue: "" });
  const [tempMaxValue, setTempMaxValue] = useState(""); // 一時的な最大値
  const [tempMinValue, setTempMinValue] = useState(""); // 一時的な最小値
  const [value, setValue] = useState(""); // "値" フィールドの状態を管理する
  const [progress, setProgress] = useState(0); // プログレスバーの進行状況を管理
  const [isUploading, setIsUploading] = useState(false); // アップロード中かどうかを管理
  const [isIndeterminate, setIsIndeterminate] = useState(false); // アニメーション表示管理

  return (
    <ChakraProvider>
      <Box m={5}>
        <Heading mb={4}>autoread</Heading>
        <VStack spacing={5} align="stretch">
          <FileUpload setUploadedFile={setUploadedFile} setFile={setFile} />
          <ContentDisplay
            uploadedFile={uploadedFile}
            file={file}
            meterData={meterData}
            setMeterData={setMeterData}
            tempMaxValue={tempMaxValue}
            setTempMaxValue={setTempMaxValue}
            tempMinValue={tempMinValue}
            setTempMinValue={setTempMinValue}
            value={value} // "値" フィールドの値を渡す
            setValue={setValue} // "値" フィールドを更新するための関数を渡す
            progress={progress} // プログレスバーの進行状況を渡す
            setProgress={setProgress} // プログレスバーを更新する関数を渡す
            isUploading={isUploading} // アップロード中の状態
            setIsUploading={setIsUploading} // アップロード中の状態を管理
            isIndeterminate={isIndeterminate} // プログレスバーのアニメーション状態
            setIsIndeterminate={setIsIndeterminate} // アニメーション状態を管理
          />
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

function ContentDisplay({
  uploadedFile,
  file,
  meterData,
  setMeterData,
  tempMaxValue,
  setTempMaxValue,
  tempMinValue,
  setTempMinValue,
  value,
  setValue,
  progress,
  setProgress,
  isUploading,
  setIsUploading,
  isIndeterminate,
  setIsIndeterminate,
}) {
  const handleAutoRead = async () => {
    if (!file) {
      alert("ファイルを選択してください。");
      return;
    }

    // 自動読み取りが押されたときに meterData を更新
    setMeterData({ maxValue: tempMaxValue, minValue: tempMinValue });

    const formData = new FormData();
    formData.append("file", file);
    formData.append("maxValue", tempMaxValue); // maxValue をフォームデータに追加
    formData.append("minValue", tempMinValue); // minValue をフォームデータに追加

    setIsUploading(true); // アップロード開始
    setIsIndeterminate(true); // アニメーション開始

    try {
      const response = await fetch('https://auto-read.onrender.com/upload', {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("サーバーエラー");
      }

      const result = await response.json(); // JSON形式でデータを受け取る

      const isNumeric = (value) => !isNaN(value) && !isNaN(parseFloat(value));
      setMeterData({
        maxValue: isNumeric(result.End) ? result.End : "",
        minValue: isNumeric(result.Start) ? result.Start : "",
      });

      // "値" フィールドにサーバーから受け取った result_value を小数点以下3桁にして表示
      setValue(parseFloat(result.result_value).toFixed(3));

      alert("ファイルアップロード成功");
    } catch (error) {
      console.error("アップロードエラー:", error);
      alert("ファイルアップロード失敗。");
    } finally {
      setIsUploading(false); // アップロード終了
      setIsIndeterminate(false); // アニメーション終了
    }
  };

  return (
    <HStack align="start" spacing={10}>
      <ImageDisplay uploadedFile={uploadedFile} />
      
      {/* メニュー部分にスライドアニメーションを追加 */}
      <motion.div
        initial={{ x: 0 }}  // 初期位置
        animate={uploadedFile ? { x: 100 } : { x: 0 }}  // 写真がアップロードされたら右にスライド
        transition={{ duration: 0.5 }}  // アニメーション時間
      >
        <MeterForm
          handleAutoRead={handleAutoRead}
          tempMaxValue={tempMaxValue}
          setTempMaxValue={setTempMaxValue}
          tempMinValue={tempMinValue}
          setTempMinValue={setTempMinValue}
          value={value} // "値" フィールドの値を渡す
          setValue={setValue} // "値" フィールドを更新するための関数を渡す
          progress={progress} // プログレスバーの値を渡す
          isUploading={isUploading} // アップロード中の状態
          isIndeterminate={isIndeterminate} // プログレスバーのアニメーション状態
        />
      </motion.div>
    </HStack>
  );
}

function ImageDisplay({ uploadedFile }) {
  if (!uploadedFile) {
    return null;
  }
  return (
    <img
      src={uploadedFile}
      alt="アップロードされた画像"
      style={{ width: "500px", height: "500px", objectFit: "cover" }}
    />
  );
}

function MeterForm({
  handleAutoRead,
  tempMaxValue,
  setTempMaxValue,
  tempMinValue,
  setTempMinValue,
  value,
  setValue,
  progress,
  isUploading,
  isIndeterminate,
}) {
  const [meterName, setMeterName] = useState("");
  const [unit, setUnit] = useState("");

  const handleDownload = () => {
    const data = {
      meterName,
      maxValue: tempMaxValue,
      minValue: tempMinValue,
      unit,
      value,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "meterData.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <Box p={5} shadow="md" borderWidth="1px">
      <FormControl mb={4}>
        <FormLabel>メーターの名前</FormLabel>
        <Input
          type="text"
          value={meterName}
          onChange={(e) => setMeterName(e.target.value)}
        />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>最大値</FormLabel>
        <Input
          type="text"
          value={tempMaxValue}
          onChange={(e) => setTempMaxValue(e.target.value)}
        />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>最小値</FormLabel>
        <Input
          type="text"
          value={tempMinValue}
          onChange={(e) => setTempMinValue(e.target.value)}
        />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>単位</FormLabel>
        <Input
          type="text"
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
        />
      </FormControl>
      <FormControl mb={4}>
        <FormLabel>値</FormLabel>
        <Input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      </FormControl>

      {/* プログレスバー */}
      <Progress size="xs" isIndeterminate={isIndeterminate} mb={4} />

      <Button colorScheme="blue" onClick={handleDownload}>
        JSONダウンロード
      </Button>
      <Button
        colorScheme="orange"
        onClick={handleAutoRead}
        isDisabled={isUploading}
      >
        {isUploading ? "アップロード中..." : "自動読み取り"}
      </Button>
    </Box>
  );
}

export default App;
