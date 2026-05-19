'use client';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

export default function TargetsTab() {
  const targets = [
    { name: "@cironogueira", status: "Monitorado", tier: "Elite" },
  ];

  return (
    <Card className="p-4 bg-black/50 border-tactical-accent">
      <h2 className="text-xl font-bold mb-4 text-tactical-accent">Alvos Ativos</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Username</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Tier</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {targets.map((t) => (
            <TableRow key={t.name}>
              <TableCell>{t.name}</TableCell>
              <TableCell>{t.status}</TableCell>
              <TableCell>{t.tier}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
