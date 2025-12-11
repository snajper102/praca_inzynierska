import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; // POPRAWKA: Usunięto 'Link'
import apiClient from '../services/api';
import { Bar } from 'react-chartjs-2'; 
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Prosty komponent karty statystyk
const ComparisonCard = ({ title, icon, current, previous, change }) => {
  const changeColor = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
  const changeIcon = change > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down';
  
  return (
    <div className="comparison-card">
      <div className="comparison-title"><i className={icon}></i> {title}</div>
      <div className="comparison-values">
        <div className="value-item">
          <div className="value-label">Teraz</div>
          <div className="value-number">{current.toFixed(1)} <span className="value-unit">kWh</span></div>
        </div>
        <div className="value-item">
          <div className="value-label">Poprzednio</div>
          <div className="value-number">{previous.toFixed(1)} <span className="value-unit">kWh</span></div>
        </div>
      </div>
      <div className={`change-indicator ${changeColor}`}>
        {change !== 0 ? <i className={changeIcon}></i> : <i className="fas fa-equals"></i>}
        {change.toFixed(1)}%
      </div>
    </div>
  );
};

const HouseDetail = () => {
  const { houseId } = useParams();
  const [house, setHouse] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [{
      label: 'Zużycie w tym m-cu (kWh)',
      data: [],
      backgroundColor: 'rgba(59, 130, 246, 0.5)',
      borderColor: '#3b82f6',
      borderWidth: 1,
    }]
  });

  useEffect(() => {
    setLoading(true);
    const fetchHouse = apiClient.get(`/user/houses/${houseId}/`);
    const fetchStats = apiClient.get(`/user/houses/${houseId}/statistics/`);

    Promise.all([fetchHouse, fetchStats])
      .then(([houseRes, statsRes]) => {
        setHouse(houseRes.data);
        setStats(statsRes.data);

        // Aktualizujemy stan wykresu
        setChartData({
          labels: statsRes.data.sensor_rankings.map(s => s.sensor_name),
          datasets: [{
            label: 'Zużycie w tym m-cu (kWh)',
            data: statsRes.data.sensor_rankings.map(s => s.kwh),
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
            borderColor: '#3b82f6',
            borderWidth: 1,
          }]
        });

        setLoading(false);
      })
      .catch(err => {
        console.error("Błąd pobierania danych domu:", err);
        setError("Nie można załadować danych.");
        setLoading(false);
      });
  }, [houseId]);

  if (loading) return <div className="container">Ładowanie statystyk...</div>;
  if (error) return <div className="container error-message">{error}</div>;
  if (!house || !stats) return null;

  return (
    <div className="comparison-container">
      <div className="comparison-header">
        <h1><i className="fas fa-chart-bar"></i> Porównania i statystyki - {house.name}</h1>
      </div>

      <div className="comparison-grid">
        <ComparisonCard 
          title="Dziś vs Wczoraj" 
          icon="fas fa-calendar-day" 
          current={stats.day_comparison.current}
          previous={stats.day_comparison.previous}
          change={stats.day_comparison.change_percent}
        />
        <ComparisonCard 
          title="Ten tydzień vs Poprzedni" 
          icon="fas fa-calendar-week" 
          current={stats.week_comparison.current}
          previous={stats.week_comparison.previous}
          change={stats.week_comparison.change_percent}
        />
        <ComparisonCard 
          title="Ten miesiąc vs Poprzedni" 
          icon="fas fa-calendar-alt" 
          current={stats.month_comparison.current}
          previous={stats.month_comparison.previous}
          change={stats.month_comparison.change_percent}
        />
      </div>
      
      <div className="prediction-section">
        <h2><i className="fas fa-crystal-ball"></i> Predykcja końca miesiąca</h2>
        <div className="prediction-grid">
          <div className="prediction-item">
            <label>Przewidywane zużycie</label>
            <div className="value">{stats.prediction.predicted_kwh.toFixed(1)} kWh</div>
          </div>
          <div className="prediction-item">
            <label>Przewidywany koszt</label>
            <div className="value">{stats.prediction.predicted_cost.toFixed(2)} PLN</div>
          </div>
          <div className="prediction-item">
            <label>Średnia dzienna</label>
            <div className="value">{stats.prediction.daily_average.toFixed(1)} kWh</div>
          </div>
        </div>
      </div>

      <div className="ranking-section">
        <h2 className="ranking-header"><i className="fas fa-trophy"></i> Ranking czujników (zużycie w miesiącu)</h2>
        <div className="chart-container" style={{ height: '300px', marginBottom: '2rem' }}>
          <Bar data={chartData} options={{ responsive: true, maintainAspectRatio: false }} />
        </div>
        <div className="ranking-list">
          {stats.sensor_rankings.map((item, index) => (
            <div className="ranking-item" key={item.sensor_id}>
              <div className={`rank-number top${index + 1}`}>{index + 1}</div>
              <div className="rank-info">
                <div className="rank-name">{item.sensor_name}</div>
                <div className="rank-location">{item.location || 'Brak lokalizacji'}</div>
              </div>
              <div className="rank-value">
                <div className="rank-kwh">{item.kwh} kWh</div>
                <div className="rank-cost">{item.cost.toFixed(2)} PLN</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HouseDetail;
