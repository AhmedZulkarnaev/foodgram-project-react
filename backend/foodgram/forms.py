from django import forms


class IngredientRecipeFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        ingredients = [
            form.cleaned_data.get(
                'ingredient'
            ) for form in self.forms if form.cleaned_data.get('ingredient')
        ]
        if not ingredients:
            raise forms.ValidationError('Должен быть хотя бы один ингредиент')
