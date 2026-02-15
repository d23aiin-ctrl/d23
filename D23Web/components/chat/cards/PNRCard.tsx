"use client";

import { Train, Calendar, MapPin, Users, CheckCircle, Clock, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Passenger {
  booking_status: string;
  current_status: string;
  coach?: string;
  berth?: string;
}

interface PNRData {
  pnr: string;
  train_number: string;
  train_name: string;
  from_station: string;
  to_station: string;
  journey_date: string;
  class: string;
  chart_prepared: boolean;
  passengers: Passenger[];
}

// Backend ToolResult format
interface ToolResult {
  success: boolean;
  data: any;
  error?: string | null;
  tool_name?: string;
}

interface PNRCardProps {
  data: PNRData | ToolResult | any;
}

// Helper to check if data is a ToolResult
function isToolResult(data: any): data is ToolResult {
  return data && typeof data === 'object' && 'success' in data && 'data' in data;
}

// Normalize the data format
function normalizePNRData(rawData: any): PNRData | null {
  if (!rawData) return null;

  // Handle ToolResult format from backend
  if (isToolResult(rawData)) {
    if (!rawData.success || !rawData.data) return null;
    return rawData.data;
  }

  // Return as-is if it looks like valid PNR data
  if (rawData.pnr || rawData.train_number) {
    return rawData;
  }

  return null;
}

export function PNRCard({ data: rawData }: PNRCardProps) {
  // Normalize the data from ToolResult or direct format
  const data = normalizePNRData(rawData);
  if (!data) return null;
  const getStatusColor = (status: string) => {
    const s = status.toUpperCase();
    if (s.includes("CNF") || s.includes("CONFIRMED")) return "bg-green-500/20 text-green-400 border-green-500/30";
    if (s.includes("RAC")) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    if (s.includes("WL") || s.includes("WAITLIST")) return "bg-red-500/20 text-red-400 border-red-500/30";
    return "bg-neutral-100 text-neutral-500 border-neutral-300";
  };

  return (
    <Card className="bg-white rounded-xl border border-neutral-200 shadow-sm overflow-hidden">
      {/* Header with Train Info */}
      <CardHeader className="pb-3 bg-gradient-to-r from-violet-500/10 to-indigo-500/10 border-b border-neutral-200">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg font-bold text-neutral-900 flex items-center gap-2">
              <Train className="h-5 w-5 text-violet-400" />
              {data.train_name}
            </CardTitle>
            <p className="text-sm text-neutral-500 mt-1">Train #{data.train_number}</p>
          </div>
          <Badge variant="outline" className="text-xs bg-neutral-50 border-neutral-300 text-neutral-600">
            PNR: {data.pnr}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-4">
        {/* Journey Route */}
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 text-neutral-900 font-medium">
              <MapPin className="h-4 w-4 text-green-400" />
              {data.from_station}
            </div>
          </div>
          <div className="flex-shrink-0 flex items-center gap-1">
            <div className="h-[2px] w-8 bg-neutral-300"></div>
            <Train className="h-4 w-4 text-neutral-400" />
            <div className="h-[2px] w-8 bg-neutral-300"></div>
          </div>
          <div className="flex-1 text-right">
            <div className="flex items-center gap-2 justify-end text-neutral-900 font-medium">
              {data.to_station}
              <MapPin className="h-4 w-4 text-red-400" />
            </div>
          </div>
        </div>

        {/* Journey Details */}
        <div className="grid grid-cols-3 gap-3 py-3 border-y border-neutral-200">
          <div className="text-center">
            <Calendar className="h-4 w-4 mx-auto text-neutral-400 mb-1" />
            <p className="text-xs text-neutral-400">Date</p>
            <p className="text-sm font-medium text-neutral-900">{data.journey_date}</p>
          </div>
          <div className="text-center">
            <Badge variant="outline" className="mx-auto bg-violet-500/20 text-violet-600 border-violet-500/30">
              {data.class}
            </Badge>
          </div>
          <div className="text-center">
            {data.chart_prepared ? (
              <div className="flex flex-col items-center">
                <CheckCircle className="h-4 w-4 text-green-400 mb-1" />
                <p className="text-xs text-green-400">Chart Ready</p>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <Clock className="h-4 w-4 text-yellow-400 mb-1" />
                <p className="text-xs text-yellow-400">Chart Pending</p>
              </div>
            )}
          </div>
        </div>

        {/* Passengers */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-4 w-4 text-neutral-500" />
            <h4 className="text-sm font-medium text-neutral-600">Passengers ({data.passengers.length})</h4>
          </div>
          <div className="space-y-2">
            {data.passengers.map((passenger, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2 rounded-lg bg-neutral-100/50 border border-neutral-200"
              >
                <span className="text-sm text-neutral-600">Passenger {idx + 1}</span>
                <div className="flex items-center gap-2">
                  <Badge className={cn("text-xs", getStatusColor(passenger.current_status))}>
                    {passenger.current_status}
                  </Badge>
                  {passenger.coach && passenger.berth && (
                    <span className="text-xs text-neutral-400">
                      {passenger.coach}/{passenger.berth}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
