import { Card } from "../../../components/ui/Card";

type MetricItem = {
  label: string;
  value: number;
};

type MetricBreakdownProps = {
  title: string;
  description: string;
  items: MetricItem[];
  total: number;
};

export default function MetricBreakdown({
  title,
  description,
  items,
  total,
}: MetricBreakdownProps) {
  return (
    <Card title={title} description={description}>
      <div className="space-y-5">
        {items.map((item) => {
          const percentage = total > 0 ? (item.value / total) * 100 : 0;

          return (
            <div key={item.label} className="space-y-2">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-medium text-foreground">
                  {item.label}
                </p>

                <div className="text-right">
                  <span className="text-sm font-semibold text-foreground">
                    {item.value.toLocaleString("en-IN")}
                  </span>
                  <span className="ml-2 text-xs text-subtle">
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              </div>

              <div
                role="progressbar"
                aria-label={`${item.label} percentage`}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={percentage}
                className="h-2 overflow-hidden rounded-full bg-canvas-subtle"
              >
                <div
                  className="h-full rounded-full bg-brand transition-[width] duration-300"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
