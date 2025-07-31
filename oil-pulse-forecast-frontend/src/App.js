import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Line } from "@nivo/line";
import { Bar } from "@nivo/bar";
import { Box, Button, CircularProgress, Container, Grid, IconButton, Paper, Toolbar, Typography, AppBar, CssBaseline, ThemeProvider, createTheme, Fade, Alert } from "@mui/material";
import { ChevronLeft, ChevronRight, Today } from "@mui/icons-material";
import "./App.css";

/* ---------- THEME ---------- */
const darkTheme = createTheme({
  palette: { mode: "dark", primary: { main: "#bb86fc" } },
  typography: { fontFamily: `"Inter", "Roboto", "Helvetica", "Arial", sans-serif` }
});

const nivoTheme = {
  background: "transparent",
  textColor: "#fff",
  axis: { ticks: { text: { fill: "#fff", fontSize: 11 } } },
  grid: { line: { stroke: "#444" } },
  tooltip: {
    container: { background: "#222", color: "#fff", borderRadius: 8, fontSize: 12 }
  }
};

/* ---------- MAIN ---------- */
export default function App() {
  const [predictions, setPredictions] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [range, setRange] = useState({
    start: "2021-08-01",
    end: "2025-07-29"
  });

  const [visibleNews, setVisibleNews] = useState(5);

  /* Helper function to validate date strings */
  const isValidDateString = (dateStr) => {
    if (!dateStr || typeof dateStr !== "string") return false;
    const date = new Date(dateStr);
    return !isNaN(date.getTime()) && dateStr.match(/^\d{4}-\d{2}-\d{2}$/);
  };

  /* Helper function to validate numeric values */
  const isValidNumber = (value) => {
    return typeof value === "number" && !isNaN(value);
  };

  /* Helper function to convert values to float */
  const convertToFloat = (value) => {
    const floatValue = parseFloat(value);
    return isNaN(floatValue) ? null : floatValue;
  };

  /* ---------- DATA FETCH ---------- */
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [pred, sent, nws] = await Promise.all([
        axios.get("/predictions", { params: range }),
        axios.get("/sentiment", { params: range }),
        axios.get("/news", { params: { ...range, limit: visibleNews } })
      ]);

      // Process predictions data
      const filteredPredData = pred.data
        .filter((d) => isValidDateString(d.date))
        .map((d) => ({
          date: d.date,
          Actual: convertToFloat(d.Actual),
          Predicted: convertToFloat(d.Predicted)
        }))
        .filter((d) => d.Actual !== null && d.Predicted !== null);

      setPredictions([
        {
          id: "Actual",
          data: filteredPredData.map((d) => ({ x: d.date, y: d.Actual }))
        },
        {
          id: "Predicted",
          data: filteredPredData.map((d) => ({ x: d.date, y: d.Predicted }))
        }
      ]);

      // Process sentiment data
      const filteredSentData = sent.data
        .filter((s) => isValidDateString(s.date))
        .map((s) => ({
          date: s.date,
          sentiment: convertToFloat(s.sentiment)
        }))
        .filter((s) => s.sentiment !== null);

      setSentiment(filteredSentData);

      // Process news data
      setNews(
        nws.data.filter((n) => {
          const date = new Date(n.publishedAt);
          return !isNaN(date.getTime());
        })
      );
    } catch (e) {
      setError("Could not load data – is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [range, visibleNews]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  /* ---------- DATE NAV ---------- */
  const shiftRange = (months) => {
    const s = new Date(range.start);
    const e = new Date(range.end);
    s.setMonth(s.getMonth() + months);
    e.setMonth(e.getMonth() + months);
    setRange({ start: s.toISOString().split("T")[0], end: e.toISOString().split("T")[0] });
  };

  /* ---------- RENDER ---------- */
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <div className="App">
        <AppBar position="static" sx={{ bgcolor: "#111" }}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
              Oil Pulse Forecast
            </Typography>
            <IconButton onClick={() => shiftRange(-1)} color="inherit">
              <ChevronLeft />
            </IconButton>
            <IconButton onClick={() => setRange({ start: "2021-08-01", end: "2025-07-29" })} color="inherit">
              <Today />
            </IconButton>
            <IconButton onClick={() => shiftRange(1)} color="inherit">
              <ChevronRight />
            </IconButton>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ py: 3 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Fade in={!loading}>
            <Grid container spacing={3}>
              {/* PREDICTIONS */}
              <Grid item xs={12}>
                <Paper className="glass" sx={{ p: 2, height: 420 }}>
                  <Typography variant="h6" gutterBottom>
                    BiGRU Predictions vs Actual
                  </Typography>
                  {!loading && predictions.length && predictions[0].data.length ? (
                    <Line
                      data={predictions}
                      height={360}
                      theme={nivoTheme}
                      margin={{ top: 10, right: 30, bottom: 60, left: 60 }}
                      xScale={{ type: "time", format: "%Y-%m-%d", precision: "day" }}
                      xFormat="time:%Y-%m-%d"
                      yScale={{ type: "linear", min: "auto", max: "auto" }}
                      colors={["#00e676", "#bb86fc"]}
                      enableSlices="x"
                      axisBottom={{
                        format: "%b %d",
                        tickValues: "every 1 month",
                        legend: "Date",
                        legendOffset: -40,
                        legendPosition: "middle"
                      }}
                      axisLeft={{ legend: "USD", legendOffset: -50, legendPosition: "middle" }}
                    />
                  ) : !loading ? (
                    <Typography variant="body1" color="text.secondary" textAlign="center" mt={4}>
                      No prediction data available for the selected range
                    </Typography>
                  ) : (
                    <Box display="flex" height="100%" alignItems="center" justifyContent="center">
                      <CircularProgress />
                    </Box>
                  )}
                </Paper>
              </Grid>

              {/* SENTIMENT */}
              <Grid item xs={12} md={6}>
                <Paper className="glass" sx={{ p: 2, height: 320 }}>
                  <Typography variant="h6" gutterBottom>
                    Market Sentiment
                  </Typography>
                  {!loading && sentiment.length ? (
                    <Bar
                      data={sentiment.map((s) => ({ date: s.date, sentiment: s.sentiment }))}
                      keys={["sentiment"]}
                      indexBy="date"
                      height={260}
                      theme={nivoTheme}
                      margin={{ left: 50, bottom: 50 }}
                      padding={0.2}
                      colors={["#7e57c2"]}
                      axisBottom={{ tickRotation: -45, format: (value) => new Date(value).toLocaleDateString() }}
                      labelSkipWidth={12}
                    />
                  ) : !loading ? (
                    <Typography variant="body1" color="text.secondary" textAlign="center" mt={4}>
                      No sentiment data available for the selected range
                    </Typography>
                  ) : (
                    <CircularProgress />
                  )}
                </Paper>
              </Grid>

              {/* NEWS */}
              <Grid item xs={12} md={6}>
                <Paper className="glass" sx={{ p: 2, height: 320, overflow: "auto" }}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="h6">Market News</Typography>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setVisibleNews((v) => v + 5)}
                      disabled={visibleNews >= news.length}
                    >
                      Load More
                    </Button>
                  </Box>

                  {news.slice(0, visibleNews).map((a, i) => (
                    <Box
                      key={i}
                      sx={{
                        p: 1.5,
                        mb: 1,
                        borderLeft: "3px solid #bb86fc",
                        bgcolor: "rgba(255,255,255,0.05)",
                        borderRadius: 1
                      }}
                    >
                      <Typography variant="subtitle2" fontWeight={600}>
                        {a.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {a.description}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(a.publishedAt).toLocaleDateString()}
                      </Typography>
                    </Box>
                  ))}

                  {!news.length && (
                    <Typography variant="body2" color="text.secondary" textAlign="center" mt={4}>
                      No news
                    </Typography>
                  )}
                </Paper>
              </Grid>
            </Grid>
          </Fade>
        </Container>
      </div>
    </ThemeProvider>
  );
}