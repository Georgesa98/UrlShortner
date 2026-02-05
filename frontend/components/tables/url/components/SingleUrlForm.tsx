import { createLinkFormSchema } from "@/app/(user)/urls/schema";
import { DatePicker } from "@/components/ui/datePicker";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Link, FileText } from "lucide-react";
import { Control, Controller } from "react-hook-form";
import z from "zod";

interface SingleUrlFormProps {
  control: Control<z.infer<typeof createLinkFormSchema>>;
  hostname: string;
  isUpdateMode?: boolean;
}

export function SingleUrlForm({ control, hostname, isUpdateMode = false }: SingleUrlFormProps) {
  return (
    <>
      {/* Link Name */}
      <Controller
        name="name"
        control={control}
        render={({ field, fieldState }) => (
          <Field>
            <FieldLabel htmlFor={field.name} className="font-bold text-sm">
              Link Name
            </FieldLabel>
            <div className="relative">
              <Input
                {...field}
                id={field.name}
                aria-invalid={fieldState.invalid}
                className="pl-10 h-12 text-sm bg-surface"
                placeholder="My Awesome Link"
              />
              <FileText
                size={18}
                className="absolute left-3 top-1/2 text-muted-foreground -translate-y-1/2"
              />
            </div>
            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
          </Field>
        )}
      />

      {/* Destination URL */}
      <Controller
        name="long_url"
        control={control}
        render={({ field, fieldState }) => (
          <Field>
            <FieldLabel htmlFor={field.name} className="font-bold text-sm">
              Destination URL
            </FieldLabel>
            <div className="relative">
              <Input
                {...field}
                id={field.name}
                aria-invalid={fieldState.invalid}
                className="pl-10 h-12 text-sm bg-surface"
                placeholder="https://example.com/your-very-long-and-complex-url-here"
              />
              <Link
                size={18}
                className="absolute left-3 top-1/2 text-muted-foreground -translate-y-1/2"
              />
            </div>
            {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
          </Field>
        )}
      />

      <span className="font-bold text-muted-foreground text-xs uppercase tracking-wider">
        Advanced Options
      </span>
      <Separator />

      {/* Custom Alias and Expiration Date */}
      <section className="w-full flex justify-between gap-4">
        <Controller
          name="short_url"
          control={control}
          render={({ field, fieldState }) => (
            <Field className="flex-1">
              <FieldLabel htmlFor={field.name} className="font-bold text-sm">
                Custom Alias {isUpdateMode ? "" : "(Optional)"}
              </FieldLabel>
              <div className="relative">
                <span className="text-xs absolute -translate-y-1/2 top-1/2 left-3 text-muted-foreground">
                  {hostname}/
                </span>
                <Separator
                  orientation="vertical"
                  className="absolute -translate-y-1/2 top-1/2 left-18 h-6"
                />
                <Input
                  {...field}
                  id={field.name}
                  aria-invalid={fieldState.invalid}
                  className="pl-20 text-sm h-12 bg-surface"
                  placeholder="my-cool-link"
                  disabled={isUpdateMode}
                />
              </div>
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
              {isUpdateMode && (
                <p className="text-xs text-muted-foreground mt-1">
                  Short URL cannot be changed after creation
                </p>
              )}
            </Field>
          )}
        />
        <Controller
          name="expiry_date"
          control={control}
          render={({ field, fieldState }) => (
            <Field className="flex-1">
              <FieldLabel htmlFor={field.name} className="font-bold text-sm">
                Expiration Date
              </FieldLabel>
              <DatePicker
                {...field}
                id={field.name}
                aria-invalid={fieldState.invalid}
              />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
      </section>

      <Separator />
    </>
  );
}
