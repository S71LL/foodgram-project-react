from django import forms

from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        text = cleaned_data.get('text')
        cooking_time = cleaned_data.get('cooking_time')
        image = cleaned_data.get('image')
        tags = cleaned_data.get('tags')

        fields = [name, text, cooking_time, image, tags]

        if not all(field for field in fields):
            raise forms.ValidationError('Недостаточно данных')

        return cleaned_data


class RecipeIngredientForm(forms.ModelForm):

    class Meta:
        model = RecipeIngredient
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        recipe = cleaned_data.get('recipe')
        ingredient = cleaned_data.get('ingredient')
        if RecipeIngredient.objects.filter(recipe=recipe,
                                           ingredient=ingredient).exists():
            raise forms.ValidationError(
                'В этом рецепте уже есть этот ингредиент')
        return cleaned_data
