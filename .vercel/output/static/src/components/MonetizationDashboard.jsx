import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MonetizationDashboard = () => {
    const [ads, setAds] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAds = async () => {
            try {
                const response = await axios.get('/api/v1/ads');
                setAds(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Erro ao buscar anúncios, Morty! *Belch!*:", error);
                setLoading(false);
            }
        };
        fetchAds();
    }, []);

    if (loading) return <div className="text-center mt-5">Carregando monitoramento financeiro de elite... 🥒</div>;

    return (
        <div className="container mt-4">
            <h2 className="mb-4 text-primary">Monitoramento de Monetização - Sentinela Democrática</h2>
            <table className="table table-striped table-hover shadow">
                <thead className="table-dark">
                    <tr>
                        <th>ID Anúncio</th>
                        <th>Candidato</th>
                        <th>Pagador</th>
                        <th>Valor Est.</th>
                        <th>Risco de Monetização</th>
                    </tr>
                </thead>
                <tbody>
                    {ads.map((ad) => (
                        <tr key={ad.ad_id}>
                            <td className="font-monospace">{ad.ad_id}</td>
                            <td>{ad.candidato_id}</td>
                            <td>{ad.pagador}</td>
                            <td>R$ {ad.valor_min?.toFixed(2)}</td>
                            <td>
                                <span className={`badge ${ad.risco_monetizacao === 'High' ? 'bg-danger' : 'bg-success'}`}>
                                    {ad.risco_monetizacao || 'Low'}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default MonetizationDashboard;
