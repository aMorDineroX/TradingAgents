/**
 * TradingAgents Charts Library
 * Graphiques interactifs pour les données de trading
 */

class TradingCharts {
    constructor() {
        this.charts = new Map();
        this.defaultColors = {
            primary: '#2563eb',
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6',
            profit: '#10b981',
            loss: '#ef4444',
            neutral: '#6b7280'
        };
        
        // Configuration par défaut pour Chart.js
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
        Chart.defaults.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color');
        
        this.init();
    }

    init() {
        console.log('📊 TradingCharts initialized');
    }

    // ========================================
    // Graphique de prix (ligne)
    // ========================================
    
    createPriceChart(containerId, data, options = {}) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: options.label || 'Prix',
                    data: data.prices,
                    borderColor: this.defaultColors.primary,
                    backgroundColor: this.defaultColors.primary + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.defaultColors.primary,
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return `Prix: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    // ========================================
    // Graphique de performance (P&L)
    // ========================================
    
    createPerformanceChart(containerId, data, options = {}) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Portfolio',
                    data: data.portfolio,
                    borderColor: this.defaultColors.primary,
                    backgroundColor: this.defaultColors.primary + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }, {
                    label: 'Benchmark',
                    data: data.benchmark,
                    borderColor: this.defaultColors.neutral,
                    backgroundColor: 'transparent',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                const percentage = ((value - 100) / 100 * 100).toFixed(2);
                                return `${context.dataset.label}: ${percentage}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                        },
                        ticks: {
                            callback: function(value) {
                                const percentage = ((value - 100) / 100 * 100).toFixed(1);
                                return percentage + '%';
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    // ========================================
    // Graphique de répartition (secteurs)
    // ========================================
    
    createAllocationChart(containerId, data, options = {}) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const colors = [
            this.defaultColors.primary,
            this.defaultColors.success,
            this.defaultColors.warning,
            this.defaultColors.error,
            this.defaultColors.info,
            '#8b5cf6',
            '#f97316',
            '#06b6d4'
        ];

        const config = {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: colors.slice(0, data.labels.length),
                    borderWidth: 2,
                    borderColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-card')
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${percentage}%`;
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    // ========================================
    // Graphique de volume
    // ========================================
    
    createVolumeChart(containerId, data, options = {}) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Volume',
                    data: data.volumes,
                    backgroundColor: this.defaultColors.primary + '60',
                    borderColor: this.defaultColors.primary,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        callbacks: {
                            label: function(context) {
                                return `Volume: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    // ========================================
    // Graphique de drawdown
    // ========================================
    
    createDrawdownChart(containerId, data, options = {}) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Drawdown',
                    data: data.drawdown,
                    borderColor: this.defaultColors.error,
                    backgroundColor: this.defaultColors.error + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        callbacks: {
                            label: function(context) {
                                return `Drawdown: ${context.parsed.y.toFixed(2)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        max: 0,
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(1) + '%';
                            }
                        }
                    }
                },
                ...options.chartOptions
            }
        };

        const chart = new Chart(ctx, config);
        this.charts.set(containerId, chart);
        return chart;
    }

    // ========================================
    // Utilitaires
    // ========================================
    
    updateChart(containerId, newData) {
        const chart = this.charts.get(containerId);
        if (!chart) return false;

        chart.data = newData;
        chart.update('none');
        return true;
    }

    destroyChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart) {
            chart.destroy();
            this.charts.delete(containerId);
            return true;
        }
        return false;
    }

    destroyAllCharts() {
        this.charts.forEach((chart, id) => {
            chart.destroy();
        });
        this.charts.clear();
    }

    resizeChart(containerId) {
        const chart = this.charts.get(containerId);
        if (chart) {
            chart.resize();
        }
    }

    resizeAllCharts() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    // ========================================
    // Gestion des thèmes
    // ========================================
    
    updateTheme() {
        const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
        const borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color');
        
        Chart.defaults.color = textColor;
        Chart.defaults.borderColor = borderColor;
        
        this.charts.forEach(chart => {
            chart.options.scales.y.grid.color = borderColor;
            chart.update('none');
        });
    }

    // ========================================
    // Helpers pour données de trading
    // ========================================
    
    formatTradingData(rawData) {
        return {
            labels: rawData.map(item => new Date(item.date).toLocaleDateString('fr-FR')),
            prices: rawData.map(item => item.close),
            volumes: rawData.map(item => item.volume),
            high: rawData.map(item => item.high),
            low: rawData.map(item => item.low),
            open: rawData.map(item => item.open)
        };
    }

    calculatePerformance(prices, benchmark = null) {
        const performance = prices.map((price, index) => {
            return ((price - prices[0]) / prices[0]) * 100;
        });

        let benchmarkPerformance = null;
        if (benchmark) {
            benchmarkPerformance = benchmark.map((price, index) => {
                return ((price - benchmark[0]) / benchmark[0]) * 100;
            });
        }

        return {
            portfolio: performance,
            benchmark: benchmarkPerformance
        };
    }

    calculateDrawdown(prices) {
        let peak = prices[0];
        const drawdown = [];

        prices.forEach(price => {
            if (price > peak) {
                peak = price;
            }
            const dd = ((price - peak) / peak) * 100;
            drawdown.push(dd);
        });

        return drawdown;
    }
}

// Instance globale
window.tradingCharts = new TradingCharts();

// Mise à jour du thème lors du changement
document.addEventListener('themeChanged', () => {
    if (window.tradingCharts) {
        window.tradingCharts.updateTheme();
    }
});

// Redimensionnement automatique
window.addEventListener('resize', () => {
    if (window.tradingCharts) {
        setTimeout(() => {
            window.tradingCharts.resizeAllCharts();
        }, 100);
    }
});
