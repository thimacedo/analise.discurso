'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import WarRoom from "./page"; // Assumindo que WarRoom é o dashboard principal
import ForensicTab from "./components/warroom/ForensicTab";
import TargetsTab from "./components/warroom/TargetsTab";
import DossiersTab from "./components/warroom/DossiersTab";
import AlertsTab from "./components/warroom/AlertsTab";
import NetworkTab from "./components/warroom/NetworkTab";
import QueueTab from "./components/warroom/QueueTab";

export default function Dashboard() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-tactical-accent mb-6">WAR ROOM</h1>
      <Tabs defaultValue="warroom" className="w-full">
        <TabsList className="bg-black/50 border border-tactical-accent">
          <TabsTrigger value="warroom">Dashboard</TabsTrigger>
          <TabsTrigger value="forensic">Análise Forense</TabsTrigger>
          <TabsTrigger value="targets">Alvos</TabsTrigger>
          <TabsTrigger value="dossiers">Dossiês</TabsTrigger>
          <TabsTrigger value="alerts">Alertas</TabsTrigger>
          <TabsTrigger value="network">Rede</TabsTrigger>
          <TabsTrigger value="queue">Fila</TabsTrigger>
        </TabsList>
        <TabsContent value="warroom"><WarRoom /></TabsContent>
        <TabsContent value="forensic"><ForensicTab /></TabsContent>
        <TabsContent value="targets"><TargetsTab /></TabsContent>
        <TabsContent value="dossiers"><DossiersTab /></TabsContent>
        <TabsContent value="alerts"><AlertsTab /></TabsContent>
        <TabsContent value="network"><NetworkTab /></TabsContent>
        <TabsContent value="queue"><QueueTab /></TabsContent>
      </Tabs>
    </div>
  );
}
