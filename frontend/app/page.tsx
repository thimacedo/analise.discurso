import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function WarRoom() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-tactical-accent mb-6">WAR ROOM</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-black/50 border-tactical-accent">
          <CardHeader>
            <CardTitle className="text-tactical-accent">Alvos Ativos</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">46</p>
          </CardContent>
        </Card>
        {/* Adicionar mais cards conforme protótipo */}
      </div>
    </div>
  );
}
