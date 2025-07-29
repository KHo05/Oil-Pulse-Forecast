import React, { useState, useEffect } from "react";
import axios from "axios";
import { Line } from "@nivo/line";
import { Bar } from "@nivo/bar";
import { Container, Typography, Paper } from "@mui/material";
import "./App.css";

function App() {
  const [predictions, setPredictions] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [news, setNews] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/predictions").then((res) => {
      setPredictions([
        { id: "Actual", data: res.data.map((d) => ({ x: d.date, y: d.Actual })) },
        { id: "Predicted", data: res.data.map((d) => ({ x: d.date, y: d.Predicted })) },
      ]);
    });
    axios.get("http://localhost:8000/sentiment").then((res) => setSentiment(res.data));
    axios.get("http://localhost:8000/news").then((res) => setNews(res.data));
  }, []);

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Oil Price Prediction
      </Typography>
      <Paper style={{ height: 400, marginBottom: 20 }}>
        <Line
          data={predictions}
          height={400}
          width={800}
          margin={{ top: 50, right: 50, bottom: 50, left: 50 }}
          xScale={{ type: "point" }}
          yScale={{ type: "linear", min: "auto", max: "auto" }}
          axisBottom={{ legend: "Date", legendOffset: 36 }}
          axisLeft={{ legend: "Price (USD)", legendOffset: -40 }}
          legends={[{ anchor: "bottom-right", direction: "column", translateX: 100 }]}
        />
      </Paper>
      <Paper style={{ height: 400, marginBottom: 20 }}>
        <Bar
          data={sentiment.map((s) => ({ date: s.date, sentiment: s.sentiment }))}
          keys={["sentiment"]}
          indexBy="date"
          height={400}
          width={800}
          margin={{ top: 50, right: 50, bottom: 50, left: 50 }}
          axisBottom={{ legend: "Date", legendOffset: 36 }}
          axisLeft={{ legend: "Sentiment", legendOffset: -40 }}
        />
      </Paper>
      <Typography variant="h6">News Articles</Typography>
      {news.map((article, index) => (
        <Paper key={index} style={{ padding: 10, marginBottom: 10 }}>
          <Typography variant="subtitle1">{article.title}</Typography>
          <Typography>{article.description}</Typography>
          <Typography variant="caption">{article.publishedAt}</Typography>
        </Paper>
      ))}
    </Container>
  );
}

export default App;